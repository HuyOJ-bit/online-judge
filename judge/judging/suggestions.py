"""Beginner-friendly, rule-based suggestions shown with each verdict —
the way big judges pair a verdict with actionable feedback."""


def make_suggestion(language: str, verdict: str, *, failed=None,
                    compile_message: str = "", passed: int = 0, total: int = 0) -> str:
    if verdict == "AC":
        return (
            "✔ All tests passed — great job!\n"
            "Want a challenge? Try a harder problem, or re-solve this one with a "
            "faster algorithm or another language."
        )

    if verdict == "CE":
        lines = ["Your code did not compile."]
        first = "\n".join(compile_message.splitlines()[:6])
        if first:
            lines.append(f"Compiler says:\n{first}")
        if language == "py":
            lines.append(
                "Tips: check indentation (tabs vs spaces), unclosed brackets/quotes, "
                "and that you're writing Python 3 (print is a function)."
            )
        elif language == "cpp":
            lines.append(
                "Tips: missing semicolon or #include? This judge compiles with "
                "g++ -std=c++17. `#include <bits/stdc++.h>` covers most headers."
            )
        else:
            lines.append(
                "Tips: missing semicolon or header? This judge compiles with "
                "gcc -std=c11 and links the math library (-lm) automatically."
            )
        return "\n\n".join(lines)

    where = f"on test {failed.index} of {total}" if failed else ""

    if verdict == "WA":
        lines = [f"Wrong answer {where}. You passed {passed}/{total} tests."]
        if failed is not None and failed.is_sample and failed.actual_preview:
            lines.append(
                "Compare your output with the expected output shown below — "
                "look for extra text, missing newlines, or different formatting."
            )
        lines.append(
            "Common causes:\n"
            "• Output format — print exactly what is asked: no prompts like "
            "\"Enter n:\", no extra text, one answer per line if required.\n"
            "• Edge cases — smallest/largest inputs (n = 0 or 1, negatives, "
            "maximum bounds).\n"
            + ("• Integer overflow — use `long long` when values can exceed "
               "2·10⁹.\n" if language in ("c", "cpp") else "")
            + "• Reading input — read the exact number of values, in the given order."
        )
        return "\n\n".join(lines)

    if verdict == "TLE":
        lines = [f"Time limit exceeded {where}. You passed {passed}/{total} tests."]
        general = (
            "Your algorithm is probably too slow for the constraints — "
            "estimate operations: about 10⁸ simple operations ≈ 1 second. "
            "Look for a lower-complexity approach (e.g. O(n log n) instead of O(n²))."
        )
        lines.append(general)
        if language == "py":
            lines.append(
                "Python tips: read input with `import sys; data = sys.stdin.read().split()` "
                "instead of many `input()` calls; avoid deep nested loops; "
                "prefer built-ins (sum, sort, dict/set lookups)."
            )
        elif language == "cpp":
            lines.append(
                "C++ tips: add `ios_base::sync_with_stdio(false); cin.tie(nullptr);` "
                "at the start of main, and use '\\n' instead of endl."
            )
        else:
            lines.append(
                "C tips: use scanf/printf (already fast); make sure you're not "
                "recomputing work inside loops. Also check for accidental infinite loops."
            )
        return "\n\n".join(lines)

    if verdict == "MLE":
        return (
            f"Memory limit exceeded {where}.\n\n"
            "You're allocating more memory than allowed. Common causes: huge arrays "
            "sized far beyond the constraints, storing all input when you can process "
            "it streaming, or building giant strings/lists. "
            + ("In Python, prefer generators over materialized lists." if language == "py" else "")
        )

    if verdict == "RE":
        lines = [f"Runtime error {where}. You passed {passed}/{total} tests."]
        detail = (failed.detail if failed else "") or ""
        stderr = (failed.stderr_tail if failed else "") or ""
        if detail:
            lines.append(f"What happened: {detail}")
        if language == "py" and stderr:
            last = [ln for ln in stderr.strip().splitlines() if ln.strip()]
            if last:
                lines.append(f"Python said: {last[-1][:300]}")
            lines.append(
                "Common Python causes: IndexError (list index out of range), "
                "ValueError on int() of empty input, RecursionError "
                "(add `sys.setrecursionlimit(10**6)`), or reading more input than exists."
            )
        else:
            lines.append(
                "Common causes: array index out of bounds, division or modulo by zero, "
                "dereferencing bad pointers, stack overflow from deep recursion, "
                "or reading more input than is provided."
            )
        return "\n\n".join(lines)

    if verdict == "IE":
        return (
            "The judge hit an internal problem while running your code — this is on "
            "our side, not yours. Please resubmit in a minute; if it keeps happening, "
            "report it in the platform chat so an admin can take a look."
        )

    return ""
