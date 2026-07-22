"""
Seed the judge with demo content:

    python manage.py seed_demo
    python manage.py seed_demo --admin-pass "S3cret!" --demo-pass "demo1234"

Creates (idempotently):
  * superuser  admin            (default password: admin123  — CHANGE IT!)
  * demo users alice, bob       (default password: demo1234)
  * 6 problems with sample + hidden test cases
  * 1 running contest with problems A/B/C and both demo users registered
  * a few chat messages
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from chat.models import ChatMessage
from judge.models import Contest, ContestProblem, Participation, Problem, TestCase

User = get_user_model()


PROBLEMS = [
    {
        "code": "SUM01", "title": "A + B", "difficulty": "E", "tags": "math, beginner",
        "time_limit": 1.0,
        "statement": "Given two integers A and B, print their sum.\n\n"
                     "This is the classic first problem of every judge — use it to "
                     "check that reading input and printing output works.",
        "input_format": "A single line with two integers A and B separated by a space.",
        "output_format": "Print one integer — the value of A + B.",
        "constraints": "-10^9 ≤ A, B ≤ 10^9",
        "hint": "In C/C++ use long long if you want to be extra safe. "
                "In Python, int never overflows.",
        "tests": [
            ("1 2", "3", True, "1 + 2 = 3."),
            ("-5 8", "3", True, ""),
            ("1000000000 1000000000", "2000000000", False, ""),
            ("-1000000000 -1000000000", "-2000000000", False, ""),
            ("0 0", "0", False, ""),
        ],
        "editorial": "Read the two integers and print their sum — the point of this "
                     "problem is verifying your input/output pipeline.\n\n"
                     "Two classic pitfalls:\n"
                     "1. Printing anything extra (prompts like \"Enter A:\") — the judge "
                     "compares output exactly.\n"
                     "2. Range: A and B fit in 32 bits here, and so does their sum — but "
                     "using 64-bit integers (long long) costs nothing and removes all doubt.",
        "editorial_code": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    long long a, b;\n    cin >> a >> b;\n    cout << a + b << '\\n';\n    return 0;\n}\n",
        "editorial_language": "cpp",
    },
    {
        "code": "ECHO1", "title": "Say It Back", "difficulty": "E", "tags": "strings, beginner",
        "time_limit": 1.0,
        "statement": "Read a single word and print it back, wrapped in a greeting.\n\n"
                     "If the input is `World`, print `Hello, World!`.",
        "input_format": "One line with a single word (no spaces).",
        "output_format": "Print `Hello, <word>!` exactly, with the comma and exclamation mark.",
        "constraints": "1 ≤ length of the word ≤ 100. The word contains only letters and digits.",
        "hint": "Watch the exact output format — a missing comma or `!` gives Wrong Answer.",
        "tests": [
            ("World", "Hello, World!", True, ""),
            ("coder", "Hello, coder!", True, ""),
            ("a", "Hello, a!", False, ""),
            ("Codes123", "Hello, Codes123!", False, ""),
        ],
    },
    {
        "code": "ODD01", "title": "Odd or Even", "difficulty": "E", "tags": "math, beginner",
        "time_limit": 1.0,
        "statement": "You are given T integers. For each one, decide whether it is odd or even.",
        "input_format": "The first line contains T — the number of test values. "
                        "Each of the next T lines contains one integer N.",
        "output_format": "For every N print `odd` or `even` on its own line.",
        "constraints": "1 ≤ T ≤ 1000, -10^18 ≤ N ≤ 10^18",
        "hint": "Careful with negative numbers: in C/C++, (-3) % 2 is -1, not 1. "
                "Compare with 0 instead. N can exceed 32-bit range — use long long.",
        "tests": [
            ("3\n1\n2\n-7", "odd\neven\nodd", True, ""),
            ("2\n0\n999999999999999999", "even\nodd", False, ""),
            ("1\n-1000000000000000000", "even", False, ""),
        ],
    },
    {
        "code": "MAX01", "title": "Maximum of the Array", "difficulty": "E", "tags": "arrays",
        "time_limit": 1.0,
        "statement": "Given an array of N integers, print the largest value and how many "
                     "times it appears.",
        "input_format": "First line: N. Second line: N integers separated by spaces.",
        "output_format": "Print two integers separated by one space: the maximum value "
                         "and its number of occurrences.",
        "constraints": "1 ≤ N ≤ 10^5, |a_i| ≤ 10^9",
        "hint": "",
        "tests": [
            ("5\n1 3 2 3 1", "3 2", True, "The maximum is 3 and it appears twice."),
            ("1\n-7", "-7 1", False, ""),
            ("6\n-5 -5 -5 -9 -100 -5", "-5 4", False, ""),
        ],
    },
    {
        "code": "FIB01", "title": "Fibonacci, Fast Enough", "difficulty": "M", "tags": "math, dp",
        "time_limit": 1.0,
        "statement": "The Fibonacci sequence is F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).\n\n"
                     "Given n, print F(n).",
        "input_format": "A single integer n.",
        "output_format": "Print F(n).",
        "constraints": "0 ≤ n ≤ 90",
        "hint": "F(90) = 2880067194370816120 — that does NOT fit in 32 bits. Use long long "
                "in C/C++. A naive recursive solution is far too slow: use a loop.",
        "tests": [
            ("10", "55", True, ""),
            ("0", "0", False, ""),
            ("1", "1", False, ""),
            ("50", "12586269025", False, ""),
            ("90", "2880067194370816120", False, ""),
        ],
        "editorial": "Compute F(n) iteratively, keeping only the last two values — "
                     "O(n) time, O(1) memory.\n\n"
                     "Why the constraints matter:\n"
                     "• Naive recursion fib(n) = fib(n-1) + fib(n-2) is O(φ^n) — around "
                     "10^18 calls for n = 90. Far too slow.\n"
                     "• F(90) = 2880067194370816120 > 2^61, so 32-bit int overflows badly. "
                     "Use long long in C/C++ (Python ints are unbounded).\n\n"
                     "Loop from 2 to n, updating (prev, cur) → (cur, prev + cur).",
        "editorial_code": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    long long prev = 0, cur = 1;\n    if (n == 0) { cout << 0 << '\\n'; return 0; }\n    for (int i = 2; i <= n; i++) {\n        long long next = prev + cur;\n        prev = cur;\n        cur = next;\n    }\n    cout << cur << '\\n';\n    return 0;\n}\n",
        "editorial_language": "cpp",
    },
    {
        "code": "PRIME1", "title": "Count the Primes", "difficulty": "M", "tags": "math, sieve",
        "time_limit": 2.0,
        "statement": "Given N, count how many prime numbers are less than or equal to N.",
        "input_format": "A single integer N.",
        "output_format": "Print one integer — the number of primes ≤ N.",
        "constraints": "1 ≤ N ≤ 2·10^6",
        "hint": "Checking every number by trial division is too slow for the biggest tests. "
                "Use the Sieve of Eratosthenes.",
        "tests": [
            ("10", "4", True, "Primes ≤ 10: 2, 3, 5, 7."),
            ("1", "0", False, ""),
            ("100", "25", False, ""),
            ("2000000", "148933", False, ""),
        ],
        "editorial": "Trial-dividing every number up to N costs roughly O(N·√N) — "
                     "about 2·10^9 operations for N = 2·10^6. Too slow.\n\n"
                     "The Sieve of Eratosthenes does it in O(N log log N): mark every "
                     "multiple of each prime as composite, then count what survives.\n\n"
                     "Implementation notes:\n"
                     "• Start crossing out at p·p (smaller multiples were already "
                     "handled by smaller primes).\n"
                     "• In Python, use a bytearray and slice assignment — it pushes the "
                     "inner loop into C and comfortably fits the 2-second limit.",
        "editorial_code": "import sys\n\ndef main():\n    n = int(sys.stdin.readline())\n    if n < 2:\n        print(0)\n        return\n    sieve = bytearray([1]) * (n + 1)\n    sieve[0] = sieve[1] = 0\n    i = 2\n    while i * i <= n:\n        if sieve[i]:\n            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))\n        i += 1\n    print(sum(sieve))\n\nmain()\n",
        "editorial_language": "py",
    },
]


class Command(BaseCommand):
    help = "Seed demo users, problems, test cases, a contest and chat messages."

    def add_arguments(self, parser):
        parser.add_argument("--admin-pass", default="admin123")
        parser.add_argument("--demo-pass", default="demo1234")

    def handle(self, *args, **options):
        # ----- users ------------------------------------------------------
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True,
                      "email": "admin@example.com"},
        )
        if created:
            admin.set_password(options["admin_pass"])
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                f"Created superuser 'admin' (password: {options['admin_pass']}) — change it!"))
        else:
            self.stdout.write("Superuser 'admin' already exists — left untouched.")

        demo_users = []
        for name in ("alice", "bob"):
            user, created = User.objects.get_or_create(username=name)
            if created:
                user.set_password(options["demo_pass"])
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Created demo user '{name}' (password: {options['demo_pass']})"))
            demo_users.append(user)

        # ----- problems ----------------------------------------------------
        problems = {}
        for spec in PROBLEMS:
            problem, created = Problem.objects.get_or_create(
                code=spec["code"],
                defaults={
                    "title": spec["title"],
                    "statement": spec["statement"],
                    "input_format": spec["input_format"],
                    "output_format": spec["output_format"],
                    "constraints": spec["constraints"],
                    "hint": spec["hint"],
                    "difficulty": spec["difficulty"],
                    "tags": spec["tags"],
                    "time_limit": spec["time_limit"],
                    "created_by": admin,
                    "editorial": spec.get("editorial", ""),
                    "editorial_code": spec.get("editorial_code", ""),
                    "editorial_language": spec.get("editorial_language", ""),
                },
            )
            problems[spec["code"]] = problem
            if created:
                for i, (inp, out, sample, expl) in enumerate(spec["tests"], 1):
                    TestCase.objects.create(
                        problem=problem, order=i, input_data=inp + "\n",
                        expected_output=out + "\n", is_sample=sample,
                        explanation=expl,
                    )
                self.stdout.write(self.style.SUCCESS(
                    f"Created problem {problem.code} with {len(spec['tests'])} tests"))
            else:
                # Idempotent backfill: add editorials to pre-existing problems.
                if spec.get("editorial") and not problem.has_editorial:
                    problem.editorial = spec.get("editorial", "")
                    problem.editorial_code = spec.get("editorial_code", "")
                    problem.editorial_language = spec.get("editorial_language", "")
                    problem.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"Problem {problem.code}: editorial backfilled."))
                else:
                    self.stdout.write(f"Problem {problem.code} already exists — skipped.")

        # ----- contest -----------------------------------------------------
        now = timezone.now()
        contest, created = Contest.objects.get_or_create(
            slug="beginner-round-1",
            defaults={
                "title": "Beginner Round #1",
                "description": "A friendly practice round to get to know the judge.\n\n"
                               "Three problems, ICPC-style standings: solve as many as "
                               "you can; wrong tries add penalty minutes. Good luck!",
                "start_time": now - timedelta(hours=1),
                "end_time": now + timedelta(days=3),
            },
        )
        if created:
            for label, code in (("A", "SUM01"), ("B", "ECHO1"), ("C", "ODD01")):
                ContestProblem.objects.create(
                    contest=contest, problem=problems[code], label=label)
            for user in demo_users:
                Participation.objects.create(contest=contest, user=user)
            self.stdout.write(self.style.SUCCESS(
                f"Created running contest '{contest.title}' (ends {contest.end_time:%Y-%m-%d %H:%M})"))
        else:
            self.stdout.write("Contest 'beginner-round-1' already exists — skipped.")

        # ----- chat ----------------------------------------------------------
        if not ChatMessage.objects.exists():
            ChatMessage.objects.create(
                user=admin, room="global",
                content="Welcome to Online Judge! Ask anything here — and good luck in the round. 🚀")
            ChatMessage.objects.create(
                user=demo_users[0], room="global",
                content="hi everyone! excited for the beginner round")
            ChatMessage.objects.create(
                user=demo_users[1], room=f"contest-{contest.slug}",
                content="Problem A is a classic — good warmup!")
            self.stdout.write(self.style.SUCCESS("Created welcome chat messages"))

        self.stdout.write(self.style.SUCCESS("Seeding complete ✔"))
