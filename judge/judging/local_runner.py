"""
Local judging backend.

Compiles and runs submissions directly on the host with gcc / g++ /
python3, applying CPU-time, address-space and wall-clock limits via
`resource` + subprocess timeouts.

This is what makes the judge work on a FREE PythonAnywhere account
(no outbound internet required, gcc is pre-installed there).

SECURITY NOTE: code runs as the same OS user as the web app. There is
no real sandbox on shared hosting. Use for trusted audiences
(classroom, friends, practice groups) — or switch OJ_JUDGE_BACKEND to
"judge0" for untrusted public traffic.
"""
import math
import os
import resource
import shutil
import signal
import subprocess
import tempfile
import time

from django.conf import settings

from .base import (
    CompileResult,
    JudgeInternalError,
    TestOutcome,
    normalize_output,
    preview,
)

_SIGNAL_NAMES = {
    signal.SIGSEGV: "SIGSEGV (segmentation fault — invalid memory access)",
    signal.SIGFPE: "SIGFPE (floating point exception — often division by zero)",
    signal.SIGABRT: "SIGABRT (aborted — failed assertion or bad_alloc)",
    signal.SIGBUS: "SIGBUS (bus error)",
    signal.SIGKILL: "SIGKILL (killed — exceeded CPU or memory limit)",
    signal.SIGXCPU: "SIGXCPU (CPU time limit exceeded)",
    signal.SIGXFSZ: "SIGXFSZ (output file size limit exceeded)",
}


class LocalRunner:
    """One instance per submission; call compile() once, then run_test()
    per test case and/or run_custom() for trial runs."""

    def __init__(self, language: str, source_code: str, time_limit: float, memory_limit_mb: int):
        self.language = language
        self.source_code = source_code
        self.time_limit = max(0.1, float(time_limit))
        self.memory_limit_mb = int(memory_limit_mb)
        cfg = settings.LOCAL_JUDGE
        base = cfg.get("WORK_DIR") or None
        if base:
            os.makedirs(base, exist_ok=True)
        self.workdir = tempfile.mkdtemp(prefix="oj_", dir=base)
        self._cfg = cfg

    # ------------------------------------------------------------------ #
    def compile(self) -> CompileResult:
        cfg = self._cfg
        try:
            if self.language == "c":
                src = os.path.join(self.workdir, "main.c")
                with open(src, "w") as f:
                    f.write(self.source_code)
                cmd = [cfg["GCC_BIN"], "-O2", "-std=c11", "-w", src,
                       "-o", os.path.join(self.workdir, "prog"), "-lm"]
            elif self.language == "cpp":
                src = os.path.join(self.workdir, "main.cpp")
                with open(src, "w") as f:
                    f.write(self.source_code)
                cmd = [cfg["GPP_BIN"], "-O2", "-std=c++17", "-w", src,
                       "-o", os.path.join(self.workdir, "prog")]
            elif self.language == "py":
                src = os.path.join(self.workdir, "main.py")
                with open(src, "w") as f:
                    f.write(self.source_code)
                # Syntax check only — runtime errors surface per-test.
                cmd = [cfg["PYTHON_BIN"], "-m", "py_compile", src]
            else:
                raise JudgeInternalError(f"Unsupported language: {self.language}")

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=cfg["COMPILE_TIMEOUT"],
                cwd=self.workdir,
            )
            if proc.returncode != 0:
                msg = (proc.stderr or proc.stdout or "Compilation failed.").strip()
                return CompileResult(ok=False, message=msg[:8000])
            return CompileResult(ok=True)
        except FileNotFoundError as exc:
            raise JudgeInternalError(
                f"Compiler not found: {exc}. Install gcc/g++ or set OJ_GCC_BIN/OJ_GPP_BIN."
            )
        except subprocess.TimeoutExpired:
            return CompileResult(ok=False, message="Compilation timed out (20s).")

    # ------------------------------------------------------------------ #
    def _limits_preexec(self):
        """Build a preexec_fn applying rlimits inside the child process."""
        cpu_seconds = int(math.ceil(self.time_limit)) + 1
        # Python needs extra address space for the interpreter itself.
        mem_mb = self.memory_limit_mb + (192 if self.language == "py" else 16)
        mem_bytes = mem_mb * 1024 * 1024
        output_bytes = self._cfg["OUTPUT_LIMIT_BYTES"] * 4

        def set_limits():
            os.setsid()
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            resource.setrlimit(resource.RLIMIT_FSIZE, (output_bytes, output_bytes))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

        return set_limits

    def _execute(self, input_data: str):
        """Run the compiled program once.

        Returns (failure, time_ms, stdout, stderr_tail, detail) where
        failure is None when the program ran fine, else one of
        "TLE" / "MLE" / "RE".
        """
        if self.language == "py":
            cmd = [self._cfg["PYTHON_BIN"], os.path.join(self.workdir, "main.py")]
        else:
            cmd = [os.path.join(self.workdir, "prog")]

        wall_limit = self.time_limit * 2 + 1.5
        started = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                input=input_data or "",
                capture_output=True,
                text=True,
                timeout=wall_limit,
                cwd=self.workdir,
                preexec_fn=self._limits_preexec(),
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return ("TLE", int(self.time_limit * 1000), "", "",
                    f"No answer within the wall-clock limit ({wall_limit:.1f}s).")

        elapsed_ms = int((time.monotonic() - started) * 1000)
        stderr_tail = (proc.stderr or "")[-2000:]
        stdout = (proc.stdout or "")[: self._cfg["OUTPUT_LIMIT_BYTES"]]

        if proc.returncode != 0:
            # Distinguish TLE (SIGXCPU / SIGKILL after CPU limit) from real RE.
            if proc.returncode < 0:
                sig = -proc.returncode
                name = _SIGNAL_NAMES.get(sig, f"signal {sig}")
                if sig == signal.SIGXCPU:
                    return ("TLE", elapsed_ms, stdout, stderr_tail,
                            "CPU time limit exceeded.")
                if sig == signal.SIGKILL and elapsed_ms >= self.time_limit * 1000:
                    return ("TLE", elapsed_ms, stdout, stderr_tail,
                            "Killed after exceeding the CPU limit.")
                if sig == signal.SIGKILL:
                    return ("MLE", elapsed_ms, stdout, stderr_tail,
                            "Killed — most likely exceeded the memory limit.")
                return ("RE", elapsed_ms, stdout, stderr_tail,
                        f"Crashed with {name}.")
            detail = f"Exited with non-zero code {proc.returncode}."
            if self.language == "py" and "MemoryError" in stderr_tail:
                return ("MLE", elapsed_ms, stdout, stderr_tail,
                        "Python raised MemoryError (memory limit).")
            return ("RE", elapsed_ms, stdout, stderr_tail, detail)

        if elapsed_ms > self.time_limit * 1000:
            return ("TLE", elapsed_ms, stdout, stderr_tail,
                    "Finished, but slower than the time limit.")

        return (None, elapsed_ms, stdout, stderr_tail, "")

    # ------------------------------------------------------------------ #
    def run_test(self, index: int, input_data: str, expected_output: str,
                 is_sample: bool) -> TestOutcome:
        failure, elapsed_ms, stdout, stderr_tail, detail = self._execute(input_data)

        common = dict(
            index=index, time_ms=elapsed_ms, stderr_tail=stderr_tail,
            is_sample=is_sample,
            input_preview=preview(input_data) if is_sample else "",
            expected_preview=preview(expected_output) if is_sample else "",
        )
        if failure:
            return TestOutcome(verdict=failure, detail=detail, **common)

        if normalize_output(stdout) == normalize_output(expected_output):
            return TestOutcome(verdict="AC", index=index, time_ms=elapsed_ms,
                               is_sample=is_sample)
        out = TestOutcome(verdict="WA",
                          detail="Output differs from the expected answer.",
                          **common)
        if is_sample:
            out.actual_preview = preview(stdout)
        return out

    def run_custom(self, input_data: str) -> dict:
        """Trial run against arbitrary input — no comparison, raw output back."""
        failure, elapsed_ms, stdout, stderr_tail, detail = self._execute(input_data)
        return {
            "status": failure or "OK",
            "time_ms": elapsed_ms,
            "stdout": stdout[:10000],
            "stderr": stderr_tail[:2000],
            "detail": detail,
        }

    # ------------------------------------------------------------------ #
    def cleanup(self):
        shutil.rmtree(self.workdir, ignore_errors=True)
