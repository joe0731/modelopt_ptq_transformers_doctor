"""Plain-data contract model shared across stages."""

from __future__ import annotations

from dataclasses import asdict, dataclass

# Probe statuses (emitted by the prober, inside the uv env).
OK = "OK"
MISSING_MODULE = "MISSING_MODULE"
MISSING_SYMBOL = "MISSING_SYMBOL"
# Driver-level statuses (env/probe failures, never produced by the prober).
ENV_ERROR = "ENV_ERROR"
PROBE_ERROR = "PROBE_ERROR"


@dataclass(frozen=True)
class ContractRecord:
    """One transformers symbol that modelopt PTQ statically depends on."""

    module_path: str          # e.g. "transformers.models.t5.modeling_t5"; "" if unknown
    symbol: str | None        # e.g. "T5Attention"; None for dynamic registrations
    file: str                 # modelopt-relative source path
    line: int
    guarded: bool             # inside a try/except ImportError block
    dynamic: bool             # registration target discovered at runtime, not importable
    role: str                 # "quant" | "export"

    @property
    def key(self) -> str:
        return f"{self.module_path}:{self.symbol}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ContractRecord":
        return cls(**d)
