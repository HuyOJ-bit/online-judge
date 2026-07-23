<div align="center">

# 🚀 Online Judge

### A modern, lightweight, self-hosted Online Judge platform built with Django.

Practice • Compete • Learn

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)]()
[![Django](https://img.shields.io/badge/Django-4.2%20LTS-092E20?logo=django)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Linux-blue)]()
[![Status](https://img.shields.io/badge/Status-Active-success)]()

**Solve coding problems. Host contests. Judge code instantly.**

</div>

---

# ✨ Overview

Online Judge is an open-source competitive programming platform inspired by Codeforces, AtCoder, and LeetCode.

It allows educators, universities, coding clubs, and organizations to host programming contests while providing a modern environment for practicing algorithmic problem solving.

The entire platform is powered by **Django**, requiring only two Python dependencies while remaining highly extensible.

---

# 🚀 Features

## 📝 Problem Management

- Rich Markdown problem statements
- Constraints & explanations
- Input / Output specifications
- Hints
- Difficulty levels
- Tags
- Sample test cases
- Hidden judge test cases
- Per-problem time & memory limits

---

## ⚡ Online Judging

Supports

- C (C11)
- C++17
- Python 3

Verdicts

- ✅ Accepted
- ❌ Wrong Answer
- ⏱ Time Limit Exceeded
- 💾 Memory Limit Exceeded
- ⚠ Runtime Error
- 🔨 Compilation Error

Each submission includes

- execution time
- memory usage
- failed testcase
- detailed verdict explanation

---

## ▶ Run Before Submit

Execute code against

- Sample tests
- Custom input

without creating an official submission.

Similar to

- LeetCode
- Codeforces
- AtCoder

---

## 🏆 Contest System

- ICPC scoring
- Contest registration
- Countdown timer
- Hidden problems
- Automatic reveal
- Live standings
- Penalty calculation

---

## 📖 Editorial System

Editorials unlock automatically after solving a problem.

Supports

- Explanation
- Reference solution
- Multiple languages

Editorials remain hidden while contests are running.

---

## 📈 Leaderboard

Global ranking based on

- Distinct solved problems
- Acceptance rate
- Submission count

---

## 💬 Built-in Chat

- Global chat
- Contest chat
- AJAX polling
- No WebSockets required

---

## 🔐 Authentication

- Registration
- Login
- User profiles
- Solved history
- Submission statistics

---

## ⚙ Admin Dashboard

Everything is managed from Django Admin.

- Problems
- Test Cases
- Contests
- Users
- Editorials
- Submissions
- Rejudge
- Verdict statistics

---

# 🏗 Architecture

```
                +----------------+
                |    Browser     |
                +--------+-------+
                         |
                Django Templates
                         |
                +--------v--------+
                | Django Backend  |
                +--------+--------+
                         |
          +--------------+--------------+
          |                             |
     Local Judge                  Judge0 Backend
          |                             |
   gcc / g++ / python3           Judge0 REST API
          |
      SQLite / MySQL
```

---

# 🛠 Technology Stack

| Layer | Technology |
|--------|------------|
| Backend | Django 4.2 LTS |
| Language | Python 3 |
| Database | SQLite / MySQL |
| Judge | Local Runner / Judge0 |
| Editor | CodeMirror 5 |
| Frontend | Django Templates |
| Styling | Custom CSS |
| JavaScript | Vanilla JS |
| Chat | AJAX Polling |
| Deployment | WSGI |

---

# 📦 Installation

## Clone

```bash
git clone https://github.com/ragibcs/online-judge.git

cd online-judge
```

## Create Virtual Environment

```bash
python -m venv venv

source venv/bin/activate
```

Windows

```powershell
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Database

```bash
python manage.py migrate
```

---

## Seed Demo Data

```bash
python manage.py seed_demo
```

or create your own administrator

```bash
python manage.py createsuperuser
```

---

## Run

```bash
python manage.py runserver
```

Open

```
http://127.0.0.1:8000
```

---

# 🧑‍💻 Demo Accounts

| User | Password |
|------|----------|
| admin | admin123 |
| alice | demo1234 |
| bob | demo1234 |

> Change the admin password immediately after deployment.

---

# 🌍 Deployment

Production Checklist

- Set `OJ_DEBUG=0`
- Generate a secure `OJ_SECRET_KEY`
- Configure `OJ_ALLOWED_HOSTS`
- Run

```bash
python manage.py collectstatic
```

Deploy on

- PythonAnywhere
- Render
- Railway
- VPS
- Ubuntu Server
- DigitalOcean

---

# ⚙ Configuration

| Variable | Default |
|------------|------------|
| OJ_SECRET_KEY | Development Key |
| OJ_DEBUG | 1 |
| OJ_ALLOWED_HOSTS | * |
| OJ_TIME_ZONE | UTC |
| OJ_JUDGE_BACKEND | local |
| OJ_JUDGE0_URL | localhost |
| OJ_JUDGE0_AUTH_TOKEN | Optional |
| OJ_SUBMISSION_COOLDOWN | 15 |
| OJ_RUN_COOLDOWN | 10 |

---

# 🧠 Judging Backends

## Local

- Fast
- Offline
- GCC
- G++
- Python

Best for

- Universities
- Coding clubs
- Internal competitions

---

## Judge0

Secure remote execution through Judge0 REST API.

Ideal for

- Public deployments
- Internet-facing platforms
- Untrusted users

---

# 📂 Project Structure

```
onlinejudge/
├── accounts/
├── chat/
├── judge/
│   ├── judging/
│   ├── models.py
│   ├── views.py
│   └── admin.py
├── templates/
├── static/
└── manage.py
```

---

# 🔒 Security

The Local Judge **does not sandbox code**.

For public deployments, use

- Judge0
- Docker
- Firecracker
- gVisor

Always

- Disable Debug
- Use HTTPS
- Use a strong Secret Key

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository

2. Create a feature branch

3. Commit your changes

4. Push

5. Open a Pull Request

---

# ⭐ Support

If this project helps you,

please consider giving it a ⭐ on GitHub.

It motivates future development.

---

# 📄 License

Released under the **MIT License**.

---

<div align="center">

Built with ❤️ using Django

</div>
