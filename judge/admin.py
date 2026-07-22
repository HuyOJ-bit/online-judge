from django.contrib import admin, messages
from django.utils.html import format_html

from .judging import judge_submission
from .models import Contest, ContestProblem, Participation, Problem, Submission, TestCase

VERDICT_COLORS = {
    "AC": "#2f855a", "WA": "#c53030", "TLE": "#dd6b20", "MLE": "#dd6b20",
    "RE": "#b7791f", "CE": "#6b46c1", "IE": "#718096", "PD": "#718096", "JG": "#3182ce",
}


class TestCaseInline(admin.StackedInline):
    model = TestCase
    extra = 1
    fields = ("order", "is_sample", "input_data", "expected_output", "explanation")
    classes = ("collapse",)


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "difficulty", "time_limit", "memory_limit",
                    "testcase_count", "solved", "is_visible")
    list_filter = ("difficulty", "is_visible")
    search_fields = ("code", "title", "tags")
    inlines = [TestCaseInline]
    fieldsets = (
        (None, {"fields": ("code", "title", "difficulty", "tags", "is_visible")}),
        ("Statement", {"fields": ("statement", "input_format", "output_format",
                                  "constraints", "hint")}),
        ("Limits", {"fields": ("time_limit", "memory_limit")}),
        ("Editorial", {
            "classes": ("collapse",),
            "fields": ("editorial", "editorial_code", "editorial_language"),
            "description": "Unlocks for users who solved the problem; hidden for "
                           "everyone (except staff) while a contest containing "
                           "this problem is running.",
        }),
    )

    @admin.display(description="Tests")
    def testcase_count(self, obj):
        return obj.testcases.count()

    @admin.display(description="Solved by")
    def solved(self, obj):
        return obj.solved_count()

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("problem", "order", "is_sample")
    list_filter = ("is_sample", "problem")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "problem", "contest", "language",
                    "verdict_badge", "passed", "exec_time_ms", "submitted_at")
    list_filter = ("verdict", "language", "problem", "contest")
    search_fields = ("user__username", "problem__code", "problem__title")
    date_hierarchy = "submitted_at"
    readonly_fields = ("user", "problem", "contest", "language", "source_code",
                       "verdict", "exec_time_ms", "passed_tests", "total_tests",
                       "first_fail_test", "compile_message", "test_results",
                       "suggestion", "submitted_at")
    actions = ["rejudge"]

    @admin.display(description="Verdict")
    def verdict_badge(self, obj):
        return format_html(
            '<b style="color:{};">{}</b>',
            VERDICT_COLORS.get(obj.verdict, "#718096"),
            obj.get_verdict_display(),
        )

    @admin.display(description="Passed")
    def passed(self, obj):
        return f"{obj.passed_tests}/{obj.total_tests}"

    @admin.action(description="Re-judge selected submissions")
    def rejudge(self, request, queryset):
        count = 0
        for sub in queryset[:25]:  # protect the worker from huge batches
            judge_submission(sub)
            count += 1
        self.message_user(request, f"Re-judged {count} submission(s).",
                          level=messages.SUCCESS)

    def has_add_permission(self, request):
        return False


class ContestProblemInline(admin.TabularInline):
    model = ContestProblem
    extra = 1
    autocomplete_fields = ("problem",)


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "start_time", "end_time", "state",
                    "participant_count", "is_visible")
    list_filter = ("is_visible",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ContestProblemInline]

    @admin.display(description="Status")
    def state(self, obj):
        colors = {"upcoming": "#3182ce", "running": "#2f855a", "finished": "#718096"}
        return format_html('<b style="color:{};">{}</b>',
                           colors[obj.status], obj.status.title())

    @admin.display(description="Participants")
    def participant_count(self, obj):
        return obj.participations.count()


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("user", "contest", "registered_at")
    list_filter = ("contest",)
    search_fields = ("user__username",)
