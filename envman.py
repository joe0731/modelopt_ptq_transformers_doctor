"""Create throwaway uv envs and run the prober inside them."""

from __future__ import annotations

import json
import os
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

            payload = json.dumps({"records": records})
            proc = self.runner([py, "-P", self.prober_path], input=payload,
                               capture_output=True, text=True)
            if proc.returncode != 0:
                return {"status": PROBE_ERROR, "installed": None, "statuses": {}}
            try:
                out = json.loads(proc.stdout)
            except json.JSONDecodeError:
                return {"status": PROBE_ERROR, "installed": None, "statuses": {}}
            return {"status": "OK", "installed": out.get("transformers_version"),
                    "statuses": out.get("statuses", {})}
