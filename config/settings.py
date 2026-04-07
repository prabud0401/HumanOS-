"""
HumanOS Django Settings.

Reads most configuration from environment variables (loaded from dna/.env)
and identity.yaml (loaded via core.dna_loader at runtime).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load secrets from dna/.env
_env_path = BASE_DIR / "dna" / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me-in-production")

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

# --- Application Definition ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # HumanOS organs
    "organs.brain",
    "organs.heart",
    "organs.lungs",
    "organs.eyes",
    "organs.ears",
    "organs.voice",
    "organs.hands",
    "organs.skeleton",
    "organs.nervous_system",
    "organs.immune_system",
    "organs.digestive_system",
    "organs.circulatory_system",
    "organs.memory",
    "organs.endocrine",
    "organs.financial_cortex",
    "organs.reproductive",
    # Third-party
    "corsheaders",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database ---

_db_url = os.environ.get("DATABASE_URL", "")
if _db_url.startswith("postgresql://"):
    # Parse DATABASE_URL into Django format
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(_db_url)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Cache / Redis ---

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
    if REDIS_URL
    else {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# --- Celery ---

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = os.environ.get("TZ", "UTC")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# --- Static files ---

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# --- Media (uploaded artifacts, recordings, etc.) ---

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Auth ---

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization ---

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("TZ", "UTC")
USE_I18N = True
USE_TZ = True

# --- Default primary key ---

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS ---

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8000"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# --- Logging ---

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "humanos": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "humanos",
        },
    },
    "loggers": {
        "humanos": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO"},
        "django": {"handlers": ["console"], "level": "INFO"},
    },
    "root": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO"},
}

# --- HumanOS-specific settings ---

HUMANOS_DNA_PATH = os.environ.get("HUMANOS_DNA_PATH", str(BASE_DIR / "dna" / "identity.yaml"))
HUMANOS_SIGNING_KEY = os.environ.get("ENCRYPTION_KEY", "dev-key-change-in-production")
