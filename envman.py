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
    def __init__(self, prober_path, extra_deps=("torch",), uv="uv", runner=subprocess.run):
        self.prober_path = prober_path
        self.extra_deps = tuple(extra_deps)
        self.uv = uv
        self.runner = runner

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
            pkgs = [f"transformers=={version}", *self.extra_deps]
            install = self.runner([self.uv, "pip", "install", "--python", py, *pkgs],
                                  capture_output=True, text=True)
            if install.returncode != 0:
                return {"status": ENV_ERROR, "installed": None, "statuses": {}}

            # Copy the prober into the temp dir so its sys.path[0] becomes
            # venv_dir (which has no bisect.py), not the package directory.
            # This avoids the local bisect.py shadowing the stdlib bisect that
            # huggingface_hub imports, on ALL Python versions (the -P flag that
            # previously worked around this requires Python 3.11+).
            if os.path.isfile(self.prober_path):
                run_prober = os.path.join(venv_dir, "_prober.py")
                shutil.copyfile(self.prober_path, run_prober)
            else:
                run_prober = self.prober_path

            payload = json.dumps({"records": records})
            proc = self.runner([py, run_prober], input=payload,
                               capture_output=True, text=True)
            if proc.returncode != 0:
                return {"status": PROBE_ERROR, "installed": None, "statuses": {}}
            try:
                out = json.loads(proc.stdout)
            except json.JSONDecodeError:
                return {"status": PROBE_ERROR, "installed": None, "statuses": {}}
            return {"status": "OK", "installed": out.get("transformers_version"),
                    "statuses": out.get("statuses", {})}
