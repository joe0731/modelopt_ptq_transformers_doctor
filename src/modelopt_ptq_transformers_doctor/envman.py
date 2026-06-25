"""Create throwaway uv envs and run the prober inside them."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

from .models import ENV_ERROR, PROBE_ERROR


class EnvRunner:
    def __init__(self, prober_path, pkg="transformers", extra_deps=("torch",), uv="uv", runner=subprocess.run,
                 probe_structures=False):
        self.prober_path = prober_path
        self.pkg = pkg
        self.extra_deps = tuple(extra_deps)
        self.uv = uv
        self.runner = runner
        self.probe_structures = probe_structures

    def _python_path(self, venv_dir: str) -> str:
        if sys.platform == "win32":
            return os.path.join(venv_dir, "Scripts", "python.exe")
        return os.path.join(venv_dir, "bin", "python")

    def probe_version(self, version: str, records: list[dict]) -> dict:
        with tempfile.TemporaryDirectory(prefix="doctor-env-") as venv_dir:
            create = self.runner([self.uv, "venv", venv_dir],
                                 capture_output=True, text=True)
            if create.returncode != 0:
                return {"status": ENV_ERROR, "installed": None, "statuses": {}}

            py = self._python_path(venv_dir)
            pkgs = [f"{self.pkg}=={version}", *self.extra_deps]
            install = self.runner([self.uv, "pip", "install", "--python", py, *pkgs],
                                  capture_output=True, text=True)
            if install.returncode != 0:
                return {"status": ENV_ERROR, "installed": None, "statuses": {}}

            # Run the prober from a copy in a neutral temp dir so the package
            # directory is never on sys.path[0]; otherwise a package module could
            # shadow a stdlib module that transformers' deps import.
            # (Defence-in-depth: the -P flag that previously worked around this
            # requires Python 3.11+.)
            run_prober = os.path.join(venv_dir, "_prober.py")
            try:
                shutil.copyfile(self.prober_path, run_prober)
            except OSError:
                return {"status": ENV_ERROR, "installed": None, "statuses": {}}

            payload = json.dumps({"records": records, "probe_structures": self.probe_structures})
            proc = self.runner([py, run_prober], input=payload,
                               capture_output=True, text=True)
            if proc.returncode != 0:
                return {"status": PROBE_ERROR, "installed": None, "statuses": {}}
            try:
                out = json.loads(proc.stdout)
            except json.JSONDecodeError:
                return {"status": PROBE_ERROR, "installed": None, "statuses": {}}
            return {"status": "OK", "installed": out.get("transformers_version"),
                    "statuses": out.get("statuses", {}),
                    "signatures": out.get("signatures", {}),
                    "structural": out.get("structural", []),
                    "known_probes": out.get("known_probes", [])}


class SmokeEnvRunner:
    """Per-version environment for the runtime smoke probe: build a throwaway
    ``uv`` venv with modelopt + ``<target>==<version>`` + torch (and this
    package), then run ``smoke_prober`` (load → quantize → export) in it.

    ``modelopt_spec`` is the pip spec for modelopt (e.g. ``nvidia-modelopt==0.44.0``).
    ``repo_path`` is this checkout (installed ``--no-deps`` so the prober module
    is importable). Heavy by design — installs real torch/modelopt per version.
    """

    def __init__(self, *, modelopt_spec, repo_path, target_pkg="transformers",
                 extra_deps=("torch", "accelerate", "huggingface_hub"),
                 uv="uv", runner=subprocess.run):
        self.modelopt_spec = modelopt_spec
        self.repo_path = repo_path
        self.target_pkg = target_pkg
        self.extra_deps = tuple(extra_deps)
        self.uv = uv
        self.runner = runner

    def _python_path(self, venv_dir: str) -> str:
        if sys.platform == "win32":
            return os.path.join(venv_dir, "Scripts", "python.exe")
        return os.path.join(venv_dir, "bin", "python")

    def smoke_version(self, version, *, model, recipe, device="cuda",
                      trust_remote_code=False) -> dict:
        with tempfile.TemporaryDirectory(prefix="doctor-smoke-") as venv_dir:
            if self.runner([self.uv, "venv", venv_dir],
                           capture_output=True, text=True).returncode != 0:
                return {"reached": "env", "status": ENV_ERROR, "error_type": None, "error": "uv venv failed"}
            py = self._python_path(venv_dir)
            pkgs = [self.modelopt_spec, f"{self.target_pkg}=={version}", *self.extra_deps]
            if self.runner([self.uv, "pip", "install", "--python", py, *pkgs],
                           capture_output=True, text=True).returncode != 0:
                return {"reached": "env", "status": ENV_ERROR, "error_type": None,
                        "error": f"install failed: {' '.join(pkgs)}"}
            # install this package so `python -m ...smoke_prober` is importable
            if self.runner([self.uv, "pip", "install", "--python", py, "--no-deps", "-e", self.repo_path],
                           capture_output=True, text=True).returncode != 0:
                return {"reached": "env", "status": ENV_ERROR, "error_type": None, "error": "doctor install failed"}
            payload = json.dumps({"model": model, "recipe": recipe,
                                  "device": device, "trust_remote_code": trust_remote_code})
            proc = self.runner([py, "-m", "modelopt_ptq_transformers_doctor.smoke_prober"],
                               input=payload, capture_output=True, text=True)
            if proc.returncode != 0:
                tail = (proc.stderr or "")[-400:]
                return {"reached": "probe", "status": PROBE_ERROR, "error_type": None, "error": tail}
            stdout = proc.stdout or ""
            candidates = [stdout] + (stdout.strip().splitlines()[-1:])  # whole, then last line
            for text in candidates:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    continue
            return {"reached": "probe", "status": PROBE_ERROR, "error_type": None,
                    "error": stdout[-400:]}
