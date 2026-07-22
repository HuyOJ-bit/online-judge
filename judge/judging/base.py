"""Shared datatypes for judging backends."""
from dataclasses import dataclass, field


class JudgeInternalError(Exception):
    """Raised when the judge itself (not the user's code) fails."""


@dataclass
class CompileResult:
    ok: bool
    message: str = ""


@dataclass
class TestOutcome:
    index: int                 # 1-based test number
    verdict: str               # AC / WA / TLE / MLE / RE
    time_ms: int = 0
    detail: str = ""           # short human-readable note (signal, exception…)
    stderr_tail: str = ""      # last lines of stderr (for suggestions)
    is_sample: bool = False
    # Only populated for sample tests so hidden tests never leak:
    input_preview: str = ""
    expected_preview: str = ""
    actual_preview: str = ""


@dataclass
class JudgeOutput:
    compile_result: CompileResult
    outcomes: list = field(default_factory=list)


def normalize_output(text: str) -> str:
    """Standard OJ comparison: strip trailing spaces on each line and
    trailing blank lines, normalize line endings."""
    if text is None:
        return ""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [ln.rstrip() for ln in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def preview(text: str, limit: int = 400) -> str:
    text = text or ""
    if len(text) > limit:
        return text[:limit] + "\n… (truncated)"
    return text
