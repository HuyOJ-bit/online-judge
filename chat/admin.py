from django.contrib import admin
from .models import Problem, Submission

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "time_limit", "memory_limit")
    search_fields = ("title",)
    list_filter = ("time_limit",)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "problem", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "problem__title")
    date_hierarchy = "created_at"
