"""
Django settings for Online Judge.

Every deployment-specific value can be overridden with an environment
variable or with an optional `onlinejudge/local_settings.py` file.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "OJ_SECRET_KEY",
    "dev-only-insecure-key-change-me-in-production-9f2k1",
)

# DEBUG defaults to on for local development; set OJ_DEBUG=0 in production.
DEBUG = os.environ.get("OJ_DEBUG", "1") == "1"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("OJ_ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("OJ_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts.apps.AccountsConfig",
    "judge.apps.JudgeConfig",
    "chat.apps.ChatConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "onlinejudge.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "onlinejudge.wsgi.application"

# ---------------------------------------------------------------------------
# Database — SQLite by default (fine for a small judge on PythonAnywhere).
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 20},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

# ---------------------------------------------------------------------------
# I18N / TZ
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("OJ_TIME_ZONE", "UTC")  # e.g. "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# ---------------------------------------------------------------------------
# Online-judge specific settings
# ---------------------------------------------------------------------------
# Which judging backend to use:
#   "local"  — compile & run on this machine with gcc/g++/python3.
#              Works on PythonAnywhere FREE tier (no internet needed).
#              NOT sandboxed: only use when you trust your users
#              (classroom / friends), or accept the risk.
#   "judge0" — send code to a Judge0 CE server over HTTP.
#              Needs a reachable Judge0 instance (self-hosted or RapidAPI)
#              and outbound internet (paid PythonAnywhere account).
JUDGE_BACKEND = os.environ.get("OJ_JUDGE_BACKEND", "local")

# Judge0 configuration (used when JUDGE_BACKEND == "judge0")
JUDGE0_URL = os.environ.get("OJ_JUDGE0_URL", "http://localhost:2358").rstrip("/")
JUDGE0_AUTH_TOKEN = os.environ.get("OJ_JUDGE0_AUTH_TOKEN", "")       # X-Auth-Token header
JUDGE0_RAPIDAPI_KEY = os.environ.get("OJ_JUDGE0_RAPIDAPI_KEY", "")   # if using RapidAPI
JUDGE0_RAPIDAPI_HOST = os.environ.get(
    "OJ_JUDGE0_RAPIDAPI_HOST", "judge0-ce.p.rapidapi.com"
)

# Local runner configuration
LOCAL_JUDGE = {
    "COMPILE_TIMEOUT": 20,          # seconds allowed for gcc/g++
    "OUTPUT_LIMIT_BYTES": 1_000_000,  # stored/compared output cap
    "WORK_DIR": os.environ.get("OJ_JUDGE_WORK_DIR", ""),  # "" => system temp
    "PYTHON_BIN": os.environ.get("OJ_PYTHON_BIN", "python3"),
    "GCC_BIN": os.environ.get("OJ_GCC_BIN", "gcc"),
    "GPP_BIN": os.environ.get("OJ_GPP_BIN", "g++"),
}

# Seconds a user must wait between two submissions (protects free-tier CPU)
SUBMISSION_COOLDOWN_SECONDS = int(os.environ.get("OJ_SUBMISSION_COOLDOWN", "15"))

# Seconds between "Run" (test-before-submit) trial runs
RUN_COOLDOWN_SECONDS = int(os.environ.get("OJ_RUN_COOLDOWN", "10"))

# Max source size (bytes)
MAX_SOURCE_BYTES = 65536

# Production hardening (active when OJ_DEBUG=0)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

# Optional local overrides
try:
    from .local_settings import *  # noqa: F401,F403
except ImportError:
    pass

# --- Render Production Config ---
import os
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"]

if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    try:
        idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1
        MIDDLEWARE.insert(idx, "whitenoise.middleware.WhiteNoiseMiddleware")
    except ValueError:
        pass

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
        conn_health_checks=True,
    )
}
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
