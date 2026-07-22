from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("problems/", views.problem_list, name="problem_list"),
    path("problem/<slug:code>/", views.problem_detail, name="problem_detail"),
    path("problem/<slug:code>/submit/", views.submit, name="submit"),
    path("problem/<slug:code>/run/", views.run_code, name="run_code"),
    path("problem/<slug:code>/editorial/", views.problem_editorial, name="problem_editorial"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("submissions/", views.submission_list, name="submission_list"),
    path("submission/<int:pk>/", views.submission_detail, name="submission_detail"),
    path("contests/", views.contest_list, name="contest_list"),
    path("contest/<slug:slug>/", views.contest_detail, name="contest_detail"),
    path("contest/<slug:slug>/register/", views.contest_register, name="contest_register"),
    path("contest/<slug:slug>/standings/", views.contest_standings, name="contest_standings"),
]
