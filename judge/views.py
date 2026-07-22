import time as _time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import SubmissionForm
from .judging import judge_submission, run_trial
from .models import Contest, ContestProblem, Participation, Problem, Submission

STARTER_CODE = {
    "c": '#include <stdio.h>\n\nint main(void) {\n    \n    return 0;\n}\n',
    "cpp": '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(nullptr);\n    \n    return 0;\n}\n',
    "py": 'import sys\ninput = sys.stdin.readline\n\n\ndef main():\n    pass\n\n\nmain()\n',
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _user_can_view_problem(user, problem):
    if problem.is_visible:
        return True
    if user.is_authenticated and user.is_staff:
        return True
    # Hidden problems become viewable through contests that have started.
    now = timezone.now()
    cps = ContestProblem.objects.filter(problem=problem,
                                        contest__start_time__lte=now)
    for cp in cps.select_related("contest"):
        contest = cp.contest
        if contest.status == "finished":
            return True
        if contest.user_registered(user):
            return True
    return False


def _solved_problem_ids(user):
    if not user.is_authenticated:
        return set()
    return set(
        Submission.objects.filter(user=user, verdict="AC")
        .values_list("problem_id", flat=True)
    )


def _editorial_access(user, problem):
    """Can this user read the editorial?

    Returns (can_view, reason) with reason in {"", "live_contest", "not_solved"}.
    Rules: staff always; hidden for everyone while a contest containing the
    problem is running; otherwise unlocked by solving the problem.
    """
    if user.is_authenticated and user.is_staff:
        return True, ""
    now = timezone.now()
    in_live_contest = ContestProblem.objects.filter(
        problem=problem,
        contest__start_time__lte=now,
        contest__end_time__gte=now,
    ).exists()
    if in_live_contest:
        return False, "live_contest"
    if user.is_authenticated and problem.submissions.filter(
            user=user, verdict="AC").exists():
        return True, ""
    return False, "not_solved"


# --------------------------------------------------------------------------- #
# Home
# --------------------------------------------------------------------------- #
def home(request):
    now = timezone.now()
    running = Contest.objects.filter(is_visible=True, start_time__lte=now,
                                     end_time__gte=now)
    upcoming = Contest.objects.filter(is_visible=True,
                                      start_time__gt=now).order_by("start_time")[:3]
    recent_problems = Problem.objects.filter(is_visible=True).order_by("-created_at")[:6]
    recent_submissions = (
        Submission.objects.select_related("user", "problem")
        .order_by("-submitted_at")[:10]
    )
    stats = {
        "problems": Problem.objects.filter(is_visible=True).count(),
        "users": User.objects.count(),
        "submissions": Submission.objects.count(),
        "accepted": Submission.objects.filter(verdict="AC").count(),
    }
    return render(request, "home.html", {
        "running_contests": running,
        "upcoming_contests": upcoming,
        "recent_problems": recent_problems,
        "recent_submissions": recent_submissions,
        "stats": stats,
        "solved_ids": _solved_problem_ids(request.user),
    })


# --------------------------------------------------------------------------- #
# Problems
# --------------------------------------------------------------------------- #
def problem_list(request):
    qs = Problem.objects.filter(is_visible=True)
    difficulty = request.GET.get("difficulty", "")
    query = request.GET.get("q", "")
    if difficulty in ("E", "M", "H"):
        qs = qs.filter(difficulty=difficulty)
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(code__icontains=query) |
                       Q(tags__icontains=query))
    qs = qs.annotate(
        solver_count=Count("submissions__user",
                           filter=Q(submissions__verdict="AC"), distinct=True)
    )
    return render(request, "judge/problem_list.html", {
        "problems": qs,
        "difficulty": difficulty,
        "query": query,
        "solved_ids": _solved_problem_ids(request.user),
    })


def problem_detail(request, code):
    problem = get_object_or_404(Problem, code=code)
    if not _user_can_view_problem(request.user, problem):
        raise Http404("Problem not available.")

    contest = None
    contest_slug = request.GET.get("contest")
    if contest_slug:
        contest = Contest.objects.filter(slug=contest_slug).first()
        if contest and not ContestProblem.objects.filter(
                contest=contest, problem=problem).exists():
            contest = None

    samples = problem.testcases.filter(is_sample=True)
    form = SubmissionForm()
    my_last = None
    if request.user.is_authenticated:
        my_last = (problem.submissions.filter(user=request.user)
                   .order_by("-submitted_at").first())
    editorial_open, editorial_reason = _editorial_access(request.user, problem)
    return render(request, "judge/problem_detail.html", {
        "problem": problem,
        "samples": samples,
        "form": form,
        "contest": contest,
        "my_last": my_last,
        "starter_code": STARTER_CODE,
        "solved": request.user.is_authenticated and problem.submissions.filter(
            user=request.user, verdict="AC").exists(),
        "editorial_open": editorial_open,
        "editorial_reason": editorial_reason,
    })


def problem_editorial(request, code):
    problem = get_object_or_404(Problem, code=code)
    if not _user_can_view_problem(request.user, problem):
        raise Http404("Problem not available.")
    if not problem.has_editorial:
        raise Http404("No editorial for this problem yet.")
    can_view, reason = _editorial_access(request.user, problem)
    return render(request, "judge/editorial.html", {
        "problem": problem,
        "can_view": can_view,
        "reason": reason,
    })


@login_required
@require_POST
def submit(request, code):
    problem = get_object_or_404(Problem, code=code)
    if not _user_can_view_problem(request.user, problem):
        raise Http404("Problem not available.")

    form = SubmissionForm(request.POST)
    if not form.is_valid():
        for err in form.errors.values():
            messages.error(request, "; ".join(err))
        return redirect(problem.get_absolute_url())

    # Submission cooldown (protects free-tier CPU quota).
    cooldown = settings.SUBMISSION_COOLDOWN_SECONDS
    last = (Submission.objects.filter(user=request.user)
            .order_by("-submitted_at").first())
    if last:
        elapsed = (timezone.now() - last.submitted_at).total_seconds()
        if elapsed < cooldown:
            messages.error(
                request,
                f"Please wait {int(cooldown - elapsed) + 1}s before submitting again."
            )
            return redirect(problem.get_absolute_url())

    contest = None
    contest_slug = request.POST.get("contest", "")
    if contest_slug:
        contest = Contest.objects.filter(slug=contest_slug).first()
        if contest:
            valid = (contest.is_running
                     and contest.user_registered(request.user)
                     and ContestProblem.objects.filter(
                         contest=contest, problem=problem).exists())
            if not valid:
                contest = None

    submission = Submission.objects.create(
        user=request.user,
        problem=problem,
        contest=contest,
        language=form.cleaned_data["language"],
        source_code=form.cleaned_data["source_code"],
    )
    judge_submission(submission)  # synchronous — returns in a few seconds
    return redirect(submission.get_absolute_url())


@login_required
@require_POST
def run_code(request, code):
    """AJAX endpoint for the "Run" button — tests code against the sample
    tests and/or a custom input WITHOUT creating a submission."""
    problem = get_object_or_404(Problem, code=code)
    if not _user_can_view_problem(request.user, problem):
        raise Http404("Problem not available.")

    language = request.POST.get("language", "")
    if language not in dict(Submission.LANGUAGE_CHOICES):
        return JsonResponse({"ok": False, "error": "bad_language",
                             "message": "Unknown language."}, status=400)
    source = request.POST.get("source_code", "")
    if not source.strip():
        return JsonResponse({"ok": False, "error": "empty_source",
                             "message": "Write some code first — the editor is empty."},
                            status=400)
    if len(source.encode()) > settings.MAX_SOURCE_BYTES:
        return JsonResponse({"ok": False, "error": "too_large",
                             "message": "Source too large (max 64 KB)."}, status=400)

    # Light cooldown between trial runs (session-based).
    cooldown = getattr(settings, "RUN_COOLDOWN_SECONDS", 10)
    now = _time.time()
    last = request.session.get("last_trial_run_ts", 0)
    if now - last < cooldown:
        wait = int(cooldown - (now - last)) + 1
        return JsonResponse({"ok": False, "error": "cooldown",
                             "message": f"Please wait {wait}s between test runs."},
                            status=429)
    request.session["last_trial_run_ts"] = now

    custom_input = None
    if request.POST.get("has_custom") == "1":
        custom_input = request.POST.get("custom_input", "")[:20000]

    result = run_trial(problem, language, source, custom_input=custom_input)
    status = 200 if result.get("ok") or result.get("compile_message") else 500
    return JsonResponse(result, status=status)


# --------------------------------------------------------------------------- #
# Submissions
# --------------------------------------------------------------------------- #
def submission_list(request):
    qs = Submission.objects.select_related("user", "problem", "contest")
    if request.GET.get("mine") == "1":
        if not request.user.is_authenticated:
            return redirect("login")
        qs = qs.filter(user=request.user)
    username = request.GET.get("user", "")
    if username:
        qs = qs.filter(user__username=username)
    problem_code = request.GET.get("problem", "")
    if problem_code:
        qs = qs.filter(problem__code=problem_code)
    verdict = request.GET.get("verdict", "")
    if verdict:
        qs = qs.filter(verdict=verdict)

    paginator = Paginator(qs, 30)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "judge/submission_list.html", {
        "page": page,
        "verdicts": Submission.VERDICT_CHOICES,
        "current": {"mine": request.GET.get("mine", ""),
                    "user": username, "problem": problem_code,
                    "verdict": verdict},
    })


def submission_detail(request, pk):
    sub = get_object_or_404(
        Submission.objects.select_related("user", "problem", "contest"), pk=pk
    )
    can_view_source = (request.user.is_authenticated
                       and (request.user == sub.user or request.user.is_staff))
    editorial_open = False
    if sub.problem.has_editorial:
        editorial_open, _ = _editorial_access(request.user, sub.problem)
    return render(request, "judge/submission_detail.html", {
        "sub": sub,
        "can_view_source": can_view_source,
        "editorial_open": editorial_open,
    })


def leaderboard(request):
    users = (
        User.objects.annotate(
            solved=Count("submissions__problem",
                         filter=Q(submissions__verdict="AC"), distinct=True),
            total_subs=Count("submissions"),
            ac_subs=Count("submissions", filter=Q(submissions__verdict="AC")),
        )
        .filter(total_subs__gt=0)
        .order_by("-solved", "total_subs", "username")
    )
    paginator = Paginator(users, 50)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "judge/leaderboard.html", {"page": page})


# --------------------------------------------------------------------------- #
# Contests
# --------------------------------------------------------------------------- #
def contest_list(request):
    now = timezone.now()
    visible = Contest.objects.filter(is_visible=True)
    return render(request, "judge/contest_list.html", {
        "running": visible.filter(start_time__lte=now, end_time__gte=now),
        "upcoming": visible.filter(start_time__gt=now).order_by("start_time"),
        "past": visible.filter(end_time__lt=now),
    })


def contest_detail(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    if not contest.is_visible and not (request.user.is_authenticated
                                       and request.user.is_staff):
        raise Http404
    registered = contest.user_registered(request.user)
    cps = contest.contest_problems.select_related("problem")
    show_problems = contest.status != "upcoming" and (
        registered or contest.status == "finished"
        or (request.user.is_authenticated and request.user.is_staff)
    )

    solved_in_contest = set()
    attempted_in_contest = set()
    if request.user.is_authenticated and show_problems:
        subs = contest.submissions.filter(user=request.user)
        solved_in_contest = set(
            subs.filter(verdict="AC").values_list("problem_id", flat=True))
        attempted_in_contest = set(subs.values_list("problem_id", flat=True))

    return render(request, "judge/contest_detail.html", {
        "contest": contest,
        "registered": registered,
        "contest_problems": cps,
        "show_problems": show_problems,
        "solved_ids": solved_in_contest,
        "attempted_ids": attempted_in_contest,
        "participant_count": contest.participations.count(),
    })


@login_required
@require_POST
def contest_register(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    if contest.status == "finished":
        messages.error(request, "This contest has already finished.")
    else:
        _, created = Participation.objects.get_or_create(
            contest=contest, user=request.user)
        if created:
            messages.success(request, f"You are registered for “{contest.title}”.")
        else:
            messages.info(request, "You are already registered.")
    return redirect(contest.get_absolute_url())


def contest_standings(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    cps = list(contest.contest_problems.select_related("problem"))
    participants = contest.participations.select_related("user")

    subs = (contest.submissions
            .filter(submitted_at__gte=contest.start_time,
                    submitted_at__lte=contest.end_time)
            .exclude(verdict__in=["CE", "IE", "PD", "JG"])
            .order_by("submitted_at")
            .values("user_id", "problem_id", "verdict", "submitted_at"))

    # per (user, problem): wrong tries before first AC + AC minute
    cell = {}
    for s in subs:
        key = (s["user_id"], s["problem_id"])
        entry = cell.setdefault(key, {"tries": 0, "ac_minute": None})
        if entry["ac_minute"] is not None:
            continue
        if s["verdict"] == "AC":
            entry["ac_minute"] = int(
                (s["submitted_at"] - contest.start_time).total_seconds() // 60)
        else:
            entry["tries"] += 1

    rows = []
    for part in participants:
        solved, penalty, cells = 0, 0, []
        for cp in cps:
            entry = cell.get((part.user_id, cp.problem_id))
            if entry and entry["ac_minute"] is not None:
                solved += 1
                penalty += entry["ac_minute"] + contest.penalty_minutes * entry["tries"]
                cells.append({"state": "ac", "tries": entry["tries"] + 1,
                              "minute": entry["ac_minute"]})
            elif entry and entry["tries"]:
                cells.append({"state": "tried", "tries": entry["tries"]})
            else:
                cells.append({"state": "none"})
        rows.append({"user": part.user, "solved": solved,
                     "penalty": penalty, "cells": cells})

    rows.sort(key=lambda r: (-r["solved"], r["penalty"], r["user"].username))
    for i, row in enumerate(rows, 1):
        row["rank"] = i

    return render(request, "judge/standings.html", {
        "contest": contest,
        "contest_problems": cps,
        "rows": rows,
    })
