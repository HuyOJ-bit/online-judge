"""End-to-end judging engine verification. Run: python3 manage.py shell < test_judging.py"""
from django.contrib.auth.models import User

from judge.models import Contest, Problem, Submission
from judge.judging import judge_submission

alice = User.objects.get(username="alice")
bob = User.objects.get(username="bob")
sum01 = Problem.objects.get(code="SUM01")
prime1 = Problem.objects.get(code="PRIME1")
odd01 = Problem.objects.get(code="ODD01")
contest = Contest.objects.get(slug="beginner-round-1")

CASES = [
    # (name, user, problem, contest, lang, source, expected_verdict)
    ("C correct", alice, sum01, contest, "c",
     '#include <stdio.h>\nint main(void){long long a,b;scanf("%lld %lld",&a,&b);printf("%lld\\n",a+b);return 0;}',
     "AC"),
    ("C++ correct", bob, sum01, contest, "cpp",
     '#include <bits/stdc++.h>\nusing namespace std;\nint main(){long long a,b;cin>>a>>b;cout<<a+b<<"\\n";}',
     "AC"),
    ("Python correct", alice, odd01, contest, "py",
     'import sys\ndata=sys.stdin.read().split()\nt=int(data[0])\nout=[]\nfor i in range(1,t+1):\n    n=int(data[i])\n    out.append("even" if n%2==0 else "odd")\nprint("\\n".join(out))',
     "AC"),
    ("C++ wrong answer", bob, sum01, contest, "cpp",
     '#include <bits/stdc++.h>\nusing namespace std;\nint main(){long long a,b;cin>>a>>b;cout<<a-b<<"\\n";}',
     "WA"),
    ("C++ overflow WA (int)", alice, sum01, None, "cpp",
     '#include <bits/stdc++.h>\nusing namespace std;\nint main(){int a,b;cin>>a>>b;cout<<a+b<<"\\n";}',
     "WA"),
    ("Python TLE (infinite loop)", bob, sum01, None, "py",
     'while True:\n    pass',
     "TLE"),
    ("C++ compile error", alice, sum01, None, "cpp",
     'int main(){ this is not c++ }',
     "CE"),
    ("Python compile error", bob, sum01, None, "py",
     'def broken(:\n    pass',
     "CE"),
    ("Python runtime error", alice, sum01, None, "py",
     'a, b = map(int, input().split())\nprint(a // 0)',
     "RE"),
    ("C segfault RE", bob, sum01, None, "c",
     '#include <stdio.h>\nint main(void){int *p = 0; *p = 42; printf("%d", *p); return 0;}',
     "RE"),
    ("Python sieve AC (2s limit)", alice, prime1, None, "py",
     'import sys\nn=int(sys.stdin.readline())\nsieve=bytearray([1])*(n+1)\nsieve[0:2]=b"\\x00\\x00"\ni=2\nwhile i*i<=n:\n    if sieve[i]:\n        sieve[i*i::i]=bytearray(len(sieve[i*i::i]))\n    i+=1\nprint(sum(sieve))',
     "AC"),
    ("Python trial division TLE", bob, prime1, None, "py",
     'import sys\nn=int(sys.stdin.readline())\nc=0\nfor x in range(2,n+1):\n    ok=True\n    d=2\n    while d*d<=x:\n        if x%d==0: ok=False; break\n        d+=1\n    if ok: c+=1\nprint(c)',
     "TLE"),
]

print("=" * 78)
results = []
for name, user, problem, ctest, lang, src, expected in CASES:
    sub = Submission.objects.create(
        user=user, problem=problem, contest=ctest, language=lang, source_code=src
    )
    judge_submission(sub)
    ok = sub.verdict == expected
    results.append(ok)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name:34s} expected={expected:4s} got={sub.verdict:4s} "
          f"tests={sub.passed_tests}/{sub.total_tests} time={sub.exec_time_ms}ms")
    if not ok:
        print(f"       compile_message: {sub.compile_message[:200]}")
        print(f"       suggestion: {sub.suggestion[:200]}")

print("=" * 78)
print(f"{sum(results)}/{len(results)} judging cases behaved as expected")
if all(results):
    print("ALL JUDGING TESTS PASSED ✔")
else:
    print("SOME TESTS FAILED ✗")
