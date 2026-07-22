"""Web-layer smoke test. Run: python3 manage.py shell < test_web.py"""
from django.test import Client

from judge.models import Submission

c = Client()
results = []


def check(name, resp, expect=200, contains=None):
    ok = resp.status_code == expect
    body = ""
    if ok and contains:
        body = resp.content.decode(errors="replace")
        ok = contains in body
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name:44s} status={resp.status_code}"
          + ("" if ok else f" (expected {expect}, contains={contains!r})"))
    return resp


# ---- public pages ----
check("home page", c.get("/"), contains="Online Judge")
check("problem list", c.get("/problems/"), contains="SUM01")
check("problem detail", c.get("/problem/SUM01/"), contains="A + B")
check("problem samples shown", c.get("/problem/SUM01/"), contains="copy")
check("submissions list", c.get("/submissions/"), contains="Verdict")
check("contest list", c.get("/contests/"), contains="Beginner Round")
check("contest detail", c.get("/contest/beginner-round-1/"), contains="Register")
check("standings page", c.get("/contest/beginner-round-1/standings/"), contains="Penalty")
check("login page", c.get("/accounts/login/"), contains="Log in")
check("register page", c.get("/accounts/register/"), contains="Create your account")
check("profile page", c.get("/accounts/u/alice/"), contains="alice")
check("admin login redirect", c.get("/admin/", follow=False), expect=302)
check("chat requires login", c.get("/chat/", follow=False), expect=302)

# ---- authenticated flows ----
assert c.login(username="alice", password="demo1234"), "alice login failed"
check("chat page (logged in)", c.get("/chat/"), contains="Global chat")
check("chat messages API", c.get("/chat/api/global/messages/"), contains="Welcome to")
# respect the 2s flood protection when suites run back-to-back
import time as _t
from chat.models import ChatMessage as _CM
_last_msg = _CM.objects.filter(user__username="alice").order_by("-created_at").first()
if _last_msg:
    from django.utils import timezone as _tz
    _elapsed = (_tz.now() - _last_msg.created_at).total_seconds()
    if _elapsed < 2.5:
        _t.sleep(2.5 - _elapsed)
r = c.post("/chat/api/global/send/", {"content": "test message from smoke test"})
check("chat send API", r, contains="true")
check("contest chat page", c.get("/chat/c/beginner-round-1/"), contains="Contest chat")
check("bad chat room rejected", c.get("/chat/api/../../etc/messages/"), expect=404)
check("invalid room rejected", c.get("/chat/api/no-such-room/messages/"), expect=400)

# ---- submission via web form (cooldown-aware) ----
import time
from django.conf import settings
last = Submission.objects.filter(user__username="alice").order_by("-submitted_at").first()
if last:
    time.sleep(max(0, settings.SUBMISSION_COOLDOWN_SECONDS + 1 -
                   (__import__("django.utils.timezone", fromlist=["now"]).now()
                    - last.submitted_at).total_seconds()))
r = c.post("/problem/ECHO1/submit/", {
    "language": "py",
    "source_code": "w = input().strip()\nprint(f'Hello, {w}!')",
    "contest": "beginner-round-1",
}, follow=True)
check("submit via web form", r, contains="Accepted")
sub = Submission.objects.filter(user__username="alice",
                                problem__code="ECHO1").order_by("-submitted_at").first()
ok = sub and sub.verdict == "AC" and sub.contest and sub.contest.slug == "beginner-round-1"
results.append(bool(ok))
print(f"[{'PASS' if ok else 'FAIL'}] submission linked to contest + AC             "
      f"verdict={sub.verdict if sub else None}")

r = c.post("/problem/ECHO1/submit/", {
    "language": "py", "source_code": "print('hi')",
}, follow=True)
body = r.content.decode(errors="replace")
ok = "wait" in body.lower()
results.append(ok)
print(f"[{'PASS' if ok else 'FAIL'}] cooldown blocks rapid resubmission")

# ---- standings reflect the AC ----
check("standings show alice", c.get("/contest/beginner-round-1/standings/"),
      contains="alice")

# ---- admin as superuser ----
assert c.login(username="admin", password="admin123"), "admin login failed"
check("admin index", c.get("/admin/"), contains="Judge management")
check("admin problems", c.get("/admin/judge/problem/"), contains="SUM01")
check("admin submissions", c.get("/admin/judge/submission/"), contains="Verdict")
check("admin contests", c.get("/admin/judge/contest/"), contains="Beginner Round")
check("admin users", c.get("/admin/auth/user/"), contains="alice")
check("admin chat", c.get("/admin/chat/chatmessage/"), contains="global")
check("admin add problem form", c.get("/admin/judge/problem/add/"), contains="Expected output")

# ---- leaderboard ----
check("leaderboard page", c.get("/leaderboard/"), contains="Leaderboard")
check("leaderboard ranks users", c.get("/leaderboard/"), contains="alice")
check("nav has leaderboard link", c.get("/"), contains="/leaderboard/")

# ---- editorials (currently logged in as admin) ----
check("editorial visible to staff", c.get("/problem/FIB01/editorial/"),
      contains="iteratively")
r = c.get("/problem/ODD01/editorial/")
results.append(r.status_code == 404)
print(f"[{'PASS' if r.status_code == 404 else 'FAIL'}] no-editorial problem 404s"
      f"                          status={r.status_code}")

assert c.login(username="alice", password="demo1234")
# SUM01 is inside the RUNNING contest → hidden even though alice solved it
check("editorial hidden during live contest", c.get("/problem/SUM01/editorial/"),
      contains="hidden while a contest")
# cleanup from previous runs so the locked-state check is idempotent
from judge.models import Problem as _P
User = __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model()
_alice = User.objects.get(username="alice")
Submission.objects.filter(user=_alice, problem__code="FIB01").delete()
# FIB01 not solved by alice → locked, content must NOT leak
r = c.get("/problem/FIB01/editorial/")
body = r.content.decode(errors="replace")
ok = (r.status_code == 200 and "unlock the editorial" in body
      and "iteratively" not in body)
results.append(ok)
print(f"[{'PASS' if ok else 'FAIL'}] editorial locked until solved (no leak)")
if not ok:
    print(f"       DIAG status={r.status_code} unlock_text={'unlock the editorial' in body} "
          f"leak={'iteratively' in body} "
          f"alice_fib_subs={list(Submission.objects.filter(user=_alice, problem__code='FIB01').values_list('verdict', flat=True))}")

# solve FIB01 → unlocks
Submission.objects.get_or_create(
    user=_alice, problem=_P.objects.get(code="FIB01"), language="py",
    source_code="unlock-test", defaults={"verdict": "AC"},
)
check("editorial unlocks after AC", c.get("/problem/FIB01/editorial/"),
      contains="iteratively")
check("reference solution shown", c.get("/problem/FIB01/editorial/"),
      contains="Reference solution")
check("problem page shows editorial link", c.get("/problem/FIB01/"),
      contains="Read the editorial")

print("=" * 78)
print(f"{sum(results)}/{len(results)} web checks passed")
print("ALL WEB TESTS PASSED ✔" if all(results) else "SOME WEB TESTS FAILED ✗")
