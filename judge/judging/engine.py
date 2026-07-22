"""
Judging engine — backend-agnostic orchestration.

judge_submission(submission) runs the whole pipeline synchronously:
compile → run every test case (stopping at the first failure, like most
judges) → store verdict, per-test results and a friendly suggestion.
"""
import logging

from django.conf import settings

from .base import JudgeInternalError
from .suggestions import make_suggestion

logger = logging.getLogger(__name__)


def make_runner(language, source_code, problem):
    if settings.JUDGE_BACKEND == "judge0":
        from .judge0_client import Judge0Runner
        return Judge0Runner(language, source_code,
                            problem.time_limit, problem.memory_limit)
    from .local_runner import LocalRunner
    return LocalRunner(language, source_code,
                       problem.time_limit, problem.memory_limit)


def _get_runner(submission):
    return make_runner(submission.language, submission.source_code,
                       submission.problem)


def run_trial(problem, language, source_code, custom_input=None):
    """Test-run code before submitting: compile, run against the problem's
    SAMPLE tests, and optionally against a custom input. Creates no
    Submission — used by the "Run" button on the problem page.

    Returns a JSON-serializable dict.
    """
    runner = None
    try:
        runner = make_runner(language, source_code, problem)
        compile_result = runner.compile()
        if not compile_result.ok:
            return {"ok": False, "compile_message": compile_result.message,
                    "samples": [], "custom": None}

        samples = list(problem.testcases.filter(is_sample=True)[:5])
        sample_results = []
        for i, test in enumerate(samples, start=1):
            outcome = runner.run_test(
                index=i, input_data=test.input_data,
                expected_output=test.expected_output, is_sample=True,
            )
            if outcome.verdict == "CE":  # judge0 discovers CE on first run
                return {"ok": False,
                        "compile_message": (
                            getattr(runner, "compile_error_message", None)
                            or "Compilation failed."),
                        "samples": [], "custom": None}
            sample_results.append({
                "index": outcome.index,
                "verdict": outcome.verdict,
                "time_ms": outcome.time_ms,
                "detail": outcome.detail,
                "input": outcome.input_preview,
                "expected": outcome.expected_preview,
                "actual": (outcome.actual_preview
                           if outcome.verdict == "WA" else ""),
                "stderr": outcome.stderr_tail[:1200],
            })

        custom = None
        if custom_input is not None:
            custom = runner.run_custom(custom_input)
            if custom.get("status") == "CE":  # judge0, no samples existed
                return {"ok": False,
                        "compile_message": (
                            getattr(runner, "compile_error_message", None)
                            or custom.get("stderr") or "Compilation failed."),
                        "samples": [], "custom": None}

        return {"ok": True, "compile_message": "",
                "samples": sample_results, "custom": custom}
    except JudgeInternalError as exc:
        logger.exception("Trial run internal error")
        return {"ok": False, "error": "judge_error",
                "compile_message": str(exc)[:1000], "samples": [], "custom": None}
    except Exception:  # noqa: BLE001
        logger.exception("Unexpected trial run failure")
        return {"ok": False, "error": "judge_error",
                "compile_message": "The judge hit an internal problem — try again.",
                "samples": [], "custom": None}
    finally:
        if runner is not None:
            try:
                runner.cleanup()
            except Exception:  # noqa: BLE001
                pass


def judge_submission(submission):
    """Judge (or re-judge) a submission in place. Returns the submission."""
    tests = list(submission.problem.testcases.all())
    submission.total_tests = len(tests)
    submission.verdict = "JG"
    submission.passed_tests = 0
    submission.first_fail_test = None
    submission.compile_message = ""
    submission.test_results = []
    submission.exec_time_ms = None
    submission.save()

    if not tests:
        submission.verdict = "IE"
        submission.suggestion = (
            "This problem has no test cases yet — an admin needs to add some "
            "in the admin panel before it can be judged."
        )
        submission.save()
        return submission

    runner = None
    outcomes = []
    try:
        runner = _get_runner(submission)
        compile_result = runner.compile()
        if not compile_result.ok:
            submission.verdict = "CE"
            submission.compile_message = compile_result.message
            submission.suggestion = make_suggestion(
                submission.language, "CE", compile_message=compile_result.message
            )
            submission.save()
            return submission

        verdict = "AC"
        failed = None
        for i, test in enumerate(tests, start=1):
            outcome = runner.run_test(
                index=i,
                input_data=test.input_data,
                expected_output=test.expected_output,
                is_sample=test.is_sample,
            )
            outcomes.append(outcome)
            if outcome.verdict == "CE":  # judge0 discovers CE on first run
                submission.verdict = "CE"
                submission.compile_message = (
                    getattr(runner, "compile_error_message", None) or "Compilation failed."
                )
                submission.suggestion = make_suggestion(
                    submission.language, "CE",
                    compile_message=submission.compile_message,
                )
                submission.test_results = _serialize(outcomes[:-1])
                submission.save()
                return submission
            if outcome.verdict != "AC":
                verdict = outcome.verdict
                failed = outcome
                break

        passed = sum(1 for o in outcomes if o.verdict == "AC")
        submission.passed_tests = passed
        submission.verdict = verdict
        submission.first_fail_test = failed.index if failed else None
        times = [o.time_ms for o in outcomes if o.time_ms]
        submission.exec_time_ms = max(times) if times else 0
        submission.test_results = _serialize(outcomes)
        submission.suggestion = make_suggestion(
            submission.language, verdict, failed=failed,
            passed=passed, total=len(tests),
        )
        submission.save()
        return submission

    except JudgeInternalError as exc:
        logger.exception("Judge internal error for submission %s", submission.pk)
        submission.verdict = "IE"
        submission.compile_message = str(exc)[:2000]
        submission.suggestion = make_suggestion(submission.language, "IE")
        submission.test_results = _serialize(outcomes)
        submission.save()
        return submission
    except Exception:  # noqa: BLE001 — never let judging crash a request
        logger.exception("Unexpected judging failure for submission %s", submission.pk)
        submission.verdict = "IE"
        submission.suggestion = make_suggestion(submission.language, "IE")
        submission.save()
        return submission
    finally:
        if runner is not None:
            try:
                runner.cleanup()
            except Exception:  # noqa: BLE001
                pass


def _serialize(outcomes):
    return [
        {
            "index": o.index,
            "verdict": o.verdict,
            "time_ms": o.time_ms,
            "detail": o.detail,
            "is_sample": o.is_sample,
            "input_preview": o.input_preview,
            "expected_preview": o.expected_preview,
            "actual_preview": o.actual_preview,
        }
        for o in outcomes
    ]
