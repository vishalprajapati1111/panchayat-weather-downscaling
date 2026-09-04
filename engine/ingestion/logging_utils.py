"""
Structured fetch logging. Every data fetch writes one JSON line to
logs/fetch_log.jsonl with url, timestamp, record_count, checksum, and status.
"""
import json, hashlib, pathlib, datetime
from typing import Optional

_LOG_PATH: Optional[pathlib.Path] = None

def configure(log_path: str):
    global _LOG_PATH
    _LOG_PATH = pathlib.Path(log_path)
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_fetch(url: str, status: str, record_count: int = 0,
              bytes_: int = 0, checksum: Optional[str] = None,
              error: Optional[str] = None, **extra):
    """Append one structured line to the fetch log."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "url": url,
        "status": status,          # "ok", "cached", "error"
        "record_count": record_count,
        "bytes": bytes_,
        "checksum_md5": checksum,
        "error": error,
        **extra
    }
    if _LOG_PATH:
        with open(_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    return entry

def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()

def log_assertion(name: str, passed: bool, detail: str, **extra):
    """Append one assertion result line to the assertion log."""
    from engine.ingestion.logging_utils import _LOG_PATH
    assert_path = _LOG_PATH.parent / "assertion_log.jsonl" if _LOG_PATH else pathlib.Path("logs/assertion_log.jsonl")
    assert_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "assertion": name,
        "passed": passed,
        "detail": detail,
        **extra
    }
    with open(assert_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    status = "PASS" if passed else "FAIL"
    print(f"  [ASSERT {status}] {name}: {detail}")
    if not passed:
        raise AssertionError(f"Assertion failed: {name} — {detail}")
