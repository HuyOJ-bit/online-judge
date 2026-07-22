"""Test the /run/ endpoint. Run: python3 manage.py shell < test_run_endpoint.py"""
import json

from django.test import Client

c = Client()
results = []


def check(name, ok, extra=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name:48s} {extra}")


# anonymous → redirected to login
r = c.post("/problem/SUM01/run/", {"language": "py", "source_code": "x"})
check("run requires login", r.status_code == 302)

assert c.login(username="bob", password="demo1234")
# reset cooldown state
s = c.session
s["last_trial_run_ts"] = 0
s.save()

# good code — samples pass + custom input
r = c.post("/problem/SUM01/run/", {
    "language": "py",
    "source_code": "a,b=map(int,input().split())\nprint(a+b)",
    "has_custom": "1", "custom_input": "20 22",
})
d = json.loads(r.content)
check("run OK status", r.status_code == 200)
check("samples all AC", d["ok"] and all(s["verdict"] == "AC" for s in d["samples"]),
      f"samples={[(s['index'], s['verdict']) for s in d['samples']]}")
check("custom output correct", d["custom"]["status"] == "OK"
      and d["custom"]["stdout"].strip() == "42")

# cooldown kicks in immediately after
r = c.post("/problem/SUM01/run/", {"language": "py", "source_code": "print(1)"})
check("run cooldown enforced", r.status_code == 429)

# reset cooldown, compile error
s = c.session; s["last_trial_run_ts"] = 0; s.save()
r = c.post("/problem/SUM01/run/", {"language": "cpp", "source_code": "int main( nope"})
d = json.loads(r.content)
check("compile error reported", r.status_code == 200 and not d["ok"]
      and bool(d["compile_message"]))

# reset cooldown, WA shows expected vs actual
s = c.session; s["last_trial_run_ts"] = 0; s.save()
r = c.post("/problem/SUM01/run/", {"language": "py",
                                   "source_code": "a,b=map(int,input().split())\nprint(a-b)"})
d = json.loads(r.content)
first = d["samples"][0]
check("WA sample shows diff", first["verdict"] == "WA"
      and first["expected"].strip() and first["actual"].strip() == "-1")

# bad language rejected
s = c.session; s["last_trial_run_ts"] = 0; s.save()
r = c.post("/problem/SUM01/run/", {"language": "java", "source_code": "x"})
check("bad language rejected", r.status_code == 400)

# empty source rejected
r = c.post("/problem/SUM01/run/", {"language": "py", "source_code": "   "})
check("empty source rejected", r.status_code == 400)

print("=" * 78)
print(f"{sum(results)}/{len(results)} run-endpoint checks passed")
print("ALL RUN TESTS PASSED ✔" if all(results) else "SOME RUN TESTS FAILED ✗")
