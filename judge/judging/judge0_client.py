"""
Judge0 CE backend.

Sends each test run to a Judge0 server over HTTP and maps its statuses
onto our verdicts. Output comparison is done locally (same normalizer
as the local backend) so both backends behave identically.

Works with:
  * a self-hosted Judge0 CE instance  → set OJ_JUDGE0_URL (+ optional
    OJ_JUDGE0_AUTH_TOKEN if you configured one)
  * Judge0 CE on RapidAPI             → set OJ_JUDGE0_URL to
    https://judge0-ce.p.rapidapi.com and OJ_JUDGE0_RAPIDAPI_KEY

NOTE: On a FREE PythonAnywhere account, outbound requests only reach
whitelisted hosts through the proxy, so this backend generally needs a
paid account (any $5/mo plan) or a whitelisted endpoint.
"""
import base64
import time

import requests
from django.conf import settings

from .base import (
    CompileResult,
    JudgeInternalError,
    TestOutcome,
    normalize_output,
    preview,
)

# Judge0 CE language IDs
LANGUAGE_IDS = {
    "c": 50,     # C (GCC 9.2.0)
    "cpp": 54,   # C++ (GCC 9.2.0)
    "py": 71,    # Python (3.8.1)
}


def _b64(s: str) -> str:
    return base64.b64encode((s or "").encode()).decode()


def _unb64(s):
    if not s:
        return ""
    try:
        return base64.b64decode(s).decode(errors="replace")
    except Exception:
        return str(s)


class Judge0Runner:
    def __init__(self, language: str, source_code: str, time_limit: float, memory_limit_mb: int):
        self.language = language
        self.source_code = source_code
        self.time_limit = max(0.1, float(time_limit))
        self.memory_limit_kb = min(int(memory_limit_mb) * 1024, 512000)
        self.base_url = settings.JUDGE0_URL
        self.compile_error_message = None  # discovered on first run

    # ------------------------------------------------------------------ #
    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if settings.JUDGE0_AUTH_TOKEN:
            headers["X-Auth-Token"] = settings.JUDGE0_AUTH_TOKEN
        if settings.JUDGE0_RAPIDAPI_KEY:
            headers["X-RapidAPI-Key"] = settings.JUDGE0_RAPIDAPI_KEY
            headers["X-RapidAPI-Host"] = settings.JUDGE0_RAPIDAPI_HOST
        return headers

    def compile(self) -> CompileResult:
        # Judge0 compiles as part of each run; report success here and let
        # the engine convert a status-6 first test into a CE verdict.
        if self.language not in LANGUAGE_IDS:
            raise JudgeInternalError(f"Unsupported language: {self.language}")
        return CompileResult(ok=True)

    # ------------------------------------------------------------------ #
    def _submit_and_wait(self, stdin_data: str) -> dict:
        payload = {
            "source_code": _b64(self.source_code),
            "language_id": LANGUAGE_IDS[self.language],
            "stdin": _b64(stdin_data),
            "cpu_time_limit": round(self.time_limit, 2),
            "wall_time_limit": min(round(self.time_limit * 2 + 2, 2), 20),
            "memory_limit": self.memory_limit_kb,
        }
        try:
            resp = requests.post(
                f"{self.base_url}/submissions?base64_encoded=true&wait=true",
                json=payload, headers=self._headers(), timeout=45,
            )
        except requests.RequestException as exc:
            raise JudgeInternalError(f"Cannot reach Judge0 at {self.base_url}: {exc}")

        if resp.status_code not in (200, 201):
            raise JudgeInternalError(
                f"Judge0 returned HTTP {resp.status_code}: {resp.text[:300]}"
            )
        data = resp.json()

        # Some deployments ignore wait=true and return just a token → poll.
        if data.get("status") is None and data.get("token"):
            data = self._poll(data["token"])
        return data

    def _poll(self, token: str) -> dict:
        url = f"{self.base_url}/submissions/{token}?base64_encoded=true"
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                resp = requests.get(url, headers=self._headers(), timeout=15)
            except requests.RequestException as exc:
                raise JudgeInternalError(f"Judge0 polling failed: {exc}")
            data = resp.json()
            status_id = (data.get("status") or {}).get("id", 0)
            if status_id > 2:  # 1 = in queue, 2 = processing
                return data
            time.sleep(0.6)
        raise JudgeInternalError("Judge0 did not finish judging within 60s.")

    # ------------------------------------------------------------------ #
    def run_test(self, index: int, input_data: str, expected_output: str,
                 is_sample: bool) -> TestOutcome:
        data = self._submit_and_wait(input_data)
        status_id = (data.get("status") or {}).get("id", 13)
        stdout = _unb64(data.get("stdout"))
        stderr = _unb64(data.get("stderr"))
        compile_output = _unb64(data.get("compile_output"))
        time_ms = int(float(data.get("time") or 0) * 1000)

        common = dict(
            index=index, time_ms=time_ms, stderr_tail=stderr[-2000:],
            is_sample=is_sample,
            input_preview=preview(input_data) if is_sample else "",
            expected_preview=preview(expected_output) if is_sample else "",
        )

        if status_id == 6:  # Compilation error
            self.compile_error_message = (compile_output or "Compilation failed.")[:8000]
            return TestOutcome(verdict="CE", detail="Compilation error.", **common)
        if status_id == 5:
            return TestOutcome(verdict="TLE", detail="Time limit exceeded.", **common)
        if status_id in (7, 8, 9, 10, 11, 12):
            detail = (data.get("status") or {}).get("description", "Runtime error.")
            if "SIGKILL" in detail or status_id == 12:
                return TestOutcome(verdict="MLE" if status_id == 12 else "RE",
                                   detail=detail, **common)
            return TestOutcome(verdict="RE", detail=detail, **common)
        if status_id in (13, 14) or status_id in (1, 2):
            raise JudgeInternalError(
                f"Judge0 internal problem: {(data.get('status') or {}).get('description')}"
                f" {_unb64(data.get('message'))}"
            )

        # status 3 (Accepted = ran fine) or 4 — compare ourselves.
        if normalize_output(stdout) == normalize_output(expected_output):
            return TestOutcome(verdict="AC", **common)
        out = TestOutcome(verdict="WA",
                          detail="Output differs from the expected answer.", **common)
        if is_sample:
            out.actual_preview = preview(stdout)
        return out

    def run_custom(self, input_data: str) -> dict:
        """Trial run against arbitrary input — no comparison, raw output back."""
        data = self._submit_and_wait(input_data)
        status_id = (data.get("status") or {}).get("id", 13)
        stdout = _unb64(data.get("stdout"))
        stderr = _unb64(data.get("stderr"))
        compile_output = _unb64(data.get("compile_output"))
        time_ms = int(float(data.get("time") or 0) * 1000)
        desc = (data.get("status") or {}).get("description", "")

        if status_id == 6:
            self.compile_error_message = (compile_output or "Compilation failed.")[:8000]
            return {"status": "CE", "time_ms": 0, "stdout": "",
                    "stderr": compile_output[:2000], "detail": "Compilation error."}
        if status_id == 5:
            return {"status": "TLE", "time_ms": time_ms, "stdout": stdout[:10000],
                    "stderr": stderr[:2000], "detail": "Time limit exceeded."}
        if status_id in (7, 8, 9, 10, 11, 12):
            return {"status": "MLE" if status_id == 12 else "RE",
                    "time_ms": time_ms, "stdout": stdout[:10000],
                    "stderr": stderr[:2000], "detail": desc or "Runtime error."}
        if status_id in (13, 14, 1, 2):
            raise JudgeInternalError(f"Judge0 internal problem: {desc}")
        return {"status": "OK", "time_ms": time_ms, "stdout": stdout[:10000],
                "stderr": stderr[:2000], "detail": ""}

    def cleanup(self):
        pass
