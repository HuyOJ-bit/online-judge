# Online Judge — minimal, self-hosted

A minimalistic online judge built with **Django**. Contestants solve problems in
**C, C++ and Python**, test code before submitting, compete in contests with
ICPC-style standings, and talk in a built-in platform chat. Everything is
managed through the **Django admin panel** — problems, test cases, contests,
users, submissions.

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3 (3.9 – 3.12) |
| Web framework | **Django 4.2 LTS** — views, ORM, auth/sessions, forms, and the built-in admin as the management panel |
| Database | **SQLite** by default (single file, zero setup) — optional MySQL support is available via `DATABASES` |
| Judging engine | Custom Python engine with **two pluggable backends**: `local` (compiles/runs via `subprocess` with POSIX `resource` rlimits — `gcc -O2 -std=c11`, `g++ -O2 -std=c++17`, `python3`) and `judge0` (Judge0 CE REST API client built on `requests`) |
| Verdict pipeline | Normalized output comparison, first-failure stop, per-test results (time, signal/exception details), rule-based suggestion generator per verdict & language |
| Frontend | Server-rendered **Django templates** + one hand-written CSS design system (custom properties, no CSS framework) + **vanilla JavaScript** (no build step, no npm) |
| Code editor | **CodeMirror 5** (Material theme) from cdnjs, with jsDelivr fallback CDN and plain-textarea degradation; LeetCode-style resizable split view (ratio in `localStorage`) |
| Typography | Inter + JetBrains Mono via Google Fonts |
| Chat | AJAX polling with `fetch` every 2.5 s — no WebSockets, works on any plain WSGI host |
| Deployment | WSGI host, static files via `collectstatic` |
| Python dependencies | Exactly two: `Django==4.2.16`, `requests` |

## Features

| Area | What you get |
|---|---|
| Problems | Statement, input/output specs, constraints, hints, tags, difficulty, per-problem time & memory limits, sample + hidden test cases |
| Judging | C (gcc, C11), C++ (g++, C++17), Python 3 — verdicts: AC, WA, TLE, MLE, RE, CE with per-test results |
| Test before submit | ▶ Run button executes code against the sample tests and/or custom input instantly — no penalty, nothing recorded (like Codeforces/LeetCode) |
| Suggestions | Every verdict comes with beginner-friendly, language-specific advice (like the big judges do) |
| Contests | Registration, countdown timer, hidden problems revealed at start, ICPC standings (solved count + penalty) |
| Editorials | Admin-written solution write-ups + reference code per problem — unlock after the user gets AC, hidden for everyone while a contest containing the problem runs |
| Leaderboard | Site-wide ranking by distinct problems solved (ties → fewer submissions), with acceptance rate |
| Chat | Global room + per-contest rooms, lightweight AJAX polling (no WebSockets needed) |
| Admin panel | Add problems/test cases inline, schedule contests, browse users & submissions, re-judge action, colored verdict badges |
| Accounts | Register/login, profiles with solved problems and verdict stats |

## Quick start (local)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # demo problems, contest, users
python manage.py runserver
```

Then open http://127.0.0.1:8000 — log in as `admin` / `admin123`
(**change this password immediately**), or as demo users `alice` / `bob`
(password `demo1234`).

To start with an empty database instead, skip `seed_demo` and run
`python manage.py createsuperuser`.

## Deployment

This app runs on any WSGI host. In production:

- set `OJ_DEBUG=0`
- set a strong `OJ_SECRET_KEY`
- set `OJ_ALLOWED_HOSTS` to your domain(s)
- configure your host to import `onlinejudge.wsgi.application`
- run `python manage.py collectstatic` for static assets

## How judging works

Submissions are judged **synchronously** on submit (a few seconds), through a
pluggable backend selected with the `OJ_JUDGE_BACKEND` environment variable:

- **`local`** (default) — compiles and runs code on the same machine with
  gcc / g++ / python3, enforcing CPU-time, memory (address-space) and
output limits per test.
  ⚠️ *Not a sandbox*: submitted code runs as your own user. Use it for
  trusted audiences (your class, your friends, practice groups).
- **`judge0`** — sends each run to a [Judge0 CE](https://judge0.com) server
  over HTTP (self-hosted or RapidAPI). Untrusted code never touches your
  account. Requires outbound internet and a reachable Judge0 instance.
  Configure with `OJ_JUDGE0_URL` + `OJ_JUDGE0_AUTH_TOKEN` (or
  `OJ_JUDGE0_RAPIDAPI_KEY`).
trailing blank lines ignored), so verdicts are consistent if you switch.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `OJ_SECRET_KEY` | dev key | Django secret key — set a long random one in production |
| `OJ_DEBUG` | `1` | Set `0` in production |
| `OJ_ALLOWED_HOSTS` | `*` | e.g. `yourname.pythonanywhere.com` |
| `OJ_TIME_ZONE` | `UTC` | e.g. `Asia/Dhaka` |
| `OJ_JUDGE_BACKEND` | `local` | `local` or `judge0` |
| `OJ_JUDGE0_URL` | `http://localhost:2358` | Judge0 base URL |
| `OJ_JUDGE0_AUTH_TOKEN` | — | Judge0 auth token, if configured |
| `OJ_JUDGE0_RAPIDAPI_KEY` | — | RapidAPI key when using Judge0 on RapidAPI |
| `OJ_SUBMISSION_COOLDOWN` | `15` | Seconds between submissions per user |
| `OJ_RUN_COOLDOWN` | `10` | Seconds between "Run" test runs per user |

## Adding problems (admin)

1. `/admin/` → **Problems → Add problem**
2. Fill code (e.g. `SUM02`), title, statement, limits.
3. Add **test cases** inline: input, expected output, tick *is sample* for the
   ones shown on the problem page.
4. Save — the problem is live immediately (or untick *is visible* to keep it
   for a contest).

## Writing an editorial (admin)

1. Open the problem in `/admin/` and expand the **Editorial** section.
2. Write the explanation, optionally paste a reference solution and pick its
   language. Save.
3. Users see "📖 Editorial · 🔒 solve to unlock" on the problem page; after an
   Accepted verdict the full write-up + reference code opens up. While a
   contest containing the problem is running, the editorial stays hidden for
   everyone except staff.

## Creating a contest (admin)

1. **Contests → Add contest**: title, slug, start/end time.
2. Add contest problems inline with labels A, B, C…
3. Tip: keep contest problems `is_visible = False` so they stay hidden until
   the contest starts; they are revealed automatically to registered users.

## Project layout

```
onlinejudge/         project settings & urls
accounts/            registration, profiles
judge/               problems, contests, submissions, admin
judge/judging/       judging engine (engine, local runner, judge0 client, suggestions)
chat/                polling chat
templates/, static/  UI
```

## Security notes

- The local backend runs untrusted code with resource limits but **without
  OS-level isolation** — shared hosting does not allow real sandboxes.
  Keep the audience trusted, or switch to Judge0.
- Change the seeded `admin` password immediately (`admin123` is public
  knowledge — it is in this README).
- Set `OJ_DEBUG=0` and a real `OJ_SECRET_KEY` in production.
