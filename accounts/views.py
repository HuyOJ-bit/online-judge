from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from judge.models import Submission

from .forms import RegisterForm

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Online Judge, {user.username}!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def profile(request, username):
    person = get_object_or_404(User, username=username)
    subs = Submission.objects.filter(user=person)
    solved_qs = (subs.filter(verdict="AC")
                 .values("problem__code", "problem__title")
                 .distinct().order_by("problem__code"))
    verdict_stats = (subs.values("verdict").annotate(n=Count("id"))
                     .order_by("-n"))
    return render(request, "accounts/profile.html", {
        "person": person,
        "solved_problems": solved_qs,
        "verdict_stats": verdict_stats,
        "total_submissions": subs.count(),
        "recent": subs.select_related("problem")[:10],
    })
