from modelopt_ptq_transformers_doctor.driver import build_matrix
from modelopt_ptq_transformers_doctor.models import ContractRecord

VERSIONS = [f"4.{m}.0" for m in range(48, 53)]  # 4.48.0 .. 4.52.0


class FakeRunner:
    """OK only when the symbol is 'present' from a given version onward."""

    def __init__(self, present_from):
        self.present_from = present_from
        self.calls = 0

    def probe_version(self, version, records):
        self.calls += 1
        minor = int(version.split(".")[1])
        statuses = {}
        for r in records:
            key = f"{r['module_path']}:{r['symbol']}"
            statuses[key] = "OK" if minor >= self.present_from else "MISSING_SYMBOL"
        return {"status": "OK", "installed": version, "statuses": statuses}


def _rec():
    return ContractRecord("transformers.models.x.modeling_x", "XAttn",
                          "f.py", 1, guarded=True, dynamic=False, role="quant")


def test_matrix_reports_compatible_range():
    runner = FakeRunner(present_from=50)
    m = build_matrix([_rec()], VERSIONS, runner)
    sym = m["symbols"]["transformers.models.x.modeling_x:XAttn"]
    assert sym["compatible_ranges"] == [("4.50.0", "4.52.0")]
    assert sym["guarded"] is True and sym["role"] == "quant"


def test_probe_results_are_memoized_per_version():
    runner = FakeRunner(present_from=50)
    build_matrix([_rec(), _rec()], VERSIONS, runner)
    assert runner.calls <= len(VERSIONS)  # never re-probe a version


def test_dynamic_records_are_listed_not_probed():
    dyn = ContractRecord("", "mod_type", "f.py", 9, guarded=False, dynamic=True, role="quant")
    m = build_matrix([dyn], VERSIONS, FakeRunner(present_from=0))
    assert m["symbols"] == {}
    assert m["dynamic"] == [{"file": "f.py", "line": 9, "note": "mod_type"}]


def test_env_error_version_is_recorded_and_treated_as_not_ok():
    class ErrRunner:
        def probe_version(self, version, records):
            if version == "4.50.0":
                return {"status": "ENV_ERROR", "installed": None, "statuses": {}}
            minor = int(version.split(".")[1])
            return {"status": "OK", "installed": version,
                    "statuses": {f"{r['module_path']}:{r['symbol']}":
                                 ("OK" if minor >= 48 else "MISSING_SYMBOL") for r in records}}
    m = build_matrix([_rec()], VERSIONS, ErrRunner())
    assert m["env_errors"].get("4.50.0") == "ENV_ERROR"
