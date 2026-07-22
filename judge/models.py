from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Problem(models.Model):
    DIFFICULTY_CHOICES = [("E", "Easy"), ("M", "Medium"), ("H", "Hard")]

    code = models.SlugField(
        max_length=20,
        unique=True,
        help_text="Short unique code shown in URLs, e.g. SUM01",
    )
    title = models.CharField(max_length=200)
    statement = models.TextField(
        help_text="Problem statement. Plain text — a blank line starts a new paragraph."
    )
    input_format = models.TextField("Input", blank=True)
    output_format = models.TextField("Output", blank=True)
    constraints = models.TextField(blank=True)
    hint = models.TextField(
        blank=True, help_text="Optional hint shown behind a spoiler on the problem page."
    )
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES, default="E")
    tags = models.CharField(
        max_length=200, blank=True, help_text="Comma separated, e.g. math, greedy"
    )
    time_limit = models.FloatField(default=1.0, help_text="Seconds per test case")
    memory_limit = models.PositiveIntegerField(default=256, help_text="Megabytes")
    is_visible = models.BooleanField(
        default=True,
        help_text="Uncheck to hide from the public list (e.g. for upcoming contests).",
    )
    editorial = models.TextField(
        blank=True,
        help_text="Solution explanation. Unlocks for users who solved the problem "
                  "(hidden for everyone while a contest containing it is running).",
    )
    editorial_code = models.TextField(
        "Reference solution", blank=True,
        help_text="Optional reference implementation shown with the editorial.",
    )
    editorial_language = models.CharField(
        max_length=4, blank=True,
        choices=[("c", "C"), ("cpp", "C++"), ("py", "Python 3")],
        help_text="Language of the reference solution.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} · {self.title}"

    def get_absolute_url(self):
        return reverse("problem_detail", args=[self.code])

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def has_editorial(self):
        return bool(self.editorial or self.editorial_code)

    def solved_count(self):
        return (
            self.submissions.filter(verdict="AC")
            .values("user")
            .distinct()
            .count()
        )

    def attempted_count(self):
        return self.submissions.values("user").distinct().count()


class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="testcases"
    )
    input_data = models.TextField("Input", blank=True)
    expected_output = models.TextField("Expected output")
    is_sample = models.BooleanField(
        default=False, help_text="Sample tests are shown on the problem page."
    )
    explanation = models.TextField(
        blank=True, help_text="Optional explanation shown with sample tests."
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        kind = "sample" if self.is_sample else "hidden"
        return f"{self.problem.code} test #{self.order} ({kind})"


class Contest(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_visible = models.BooleanField(default=True)
    penalty_minutes = models.PositiveIntegerField(
        default=20, help_text="Penalty minutes added per wrong try before the AC."
    )
    problems = models.ManyToManyField(
        Problem, through="ContestProblem", related_name="contests"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("contest_detail", args=[self.slug])

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        if now <= self.end_time:
            return "running"
        return "finished"

    @property
    def is_running(self):
        return self.status == "running"

    def user_registered(self, user):
        if not user.is_authenticated:
            return False
        return self.participations.filter(user=user).exists()


class ContestProblem(models.Model):
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="contest_problems"
    )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    label = models.CharField(max_length=4, help_text="A, B, C …")
    points = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["label"]
        unique_together = [("contest", "problem"), ("contest", "label")]

    def __str__(self):
        return f"{self.contest.slug} · {self.label} · {self.problem.code}"


class Participation(models.Model):
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="participations"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("contest", "user")]

    def __str__(self):
        return f"{self.user.username} @ {self.contest.slug}"


class Submission(models.Model):
    LANGUAGE_CHOICES = [("c", "C"), ("cpp", "C++"), ("py", "Python 3")]
    VERDICT_CHOICES = [
        ("PD", "Pending"),
        ("JG", "Judging"),
        ("AC", "Accepted"),
        ("WA", "Wrong Answer"),
        ("TLE", "Time Limit Exceeded"),
        ("MLE", "Memory Limit Exceeded"),
        ("RE", "Runtime Error"),
        ("CE", "Compilation Error"),
        ("IE", "Internal Error"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="submissions"
    )
    contest = models.ForeignKey(
        Contest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submissions",
    )
    language = models.CharField(max_length=4, choices=LANGUAGE_CHOICES)
    source_code = models.TextField()
    verdict = models.CharField(max_length=4, choices=VERDICT_CHOICES, default="PD")
    exec_time_ms = models.PositiveIntegerField(null=True, blank=True)
    passed_tests = models.PositiveIntegerField(default=0)
    total_tests = models.PositiveIntegerField(default=0)
    first_fail_test = models.PositiveIntegerField(null=True, blank=True)
    compile_message = models.TextField(blank=True)
    test_results = models.JSONField(default=list, blank=True)
    suggestion = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"#{self.pk} {self.user.username} → {self.problem.code} [{self.verdict}]"

    def get_absolute_url(self):
        return reverse("submission_detail", args=[self.pk])

    @property
    def is_ac(self):
        return self.verdict == "AC"

    @property
    def verdict_class(self):
        """CSS class suffix for the verdict badge."""
        return {
            "AC": "ac",
            "WA": "wa",
            "TLE": "tle",
            "MLE": "tle",
            "RE": "re",
            "CE": "ce",
            "IE": "ie",
            "PD": "pd",
            "JG": "pd",
        }.get(self.verdict, "pd")
