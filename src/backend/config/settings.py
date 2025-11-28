"""Django settings for linkinthe.video backend."""

from __future__ import annotations

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

SITE_ID = 1

INSTALLED_APPS = [
    "user",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "video",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

DATABASES = {
    "default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        )
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "user.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

ANYMAIL = {
    "RESEND_API_KEY": env("RESEND_API_KEY", default=None),
}

PIPELINE_USE_REAL_DOWNLOAD = env.bool(
    "PIPELINE_USE_REAL_DOWNLOAD", default=False
)
PIPELINE_USE_REAL_AUDIO = env.bool(
    "PIPELINE_USE_REAL_AUDIO", default=False
)

# =============================================================================
# Provider Configuration
# =============================================================================
# Available providers:
#   transcription: mock, whisper, gemini
#   vision: mock, openai, gemini
#   llm: mock, openai, gemini
#   product_search: mock, amazon

PIPELINE_PROVIDERS = {
    "transcription": env("PIPELINE_TRANSCRIPTION_PROVIDER", default="mock"),
    "vision": env("PIPELINE_VISION_PROVIDER", default="mock"),
    "llm": env("PIPELINE_LLM_PROVIDER", default="mock"),
    "product_search": env("PIPELINE_PRODUCT_SEARCH_PROVIDER", default="mock"),
}

# Provider-specific settings
PIPELINE_LLM_MODEL = env("PIPELINE_LLM_MODEL", default="gpt-4o-mini")
PIPELINE_VISION_MODEL = env("PIPELINE_VISION_MODEL", default="gpt-4o-mini")
PIPELINE_TRANSCRIPTION_MODEL = env(
    "PIPELINE_TRANSCRIPTION_MODEL", default="whisper-1"
)

# Amazon PA-API credentials (for product search)
AMAZON_ACCESS_KEY = env("AMAZON_ACCESS_KEY", default="")
AMAZON_SECRET_KEY = env("AMAZON_SECRET_KEY", default="")
AMAZON_PARTNER_TAG = env("AMAZON_PARTNER_TAG", default="")

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env("GOOGLE_CLIENT_ID", default=""),
            "secret": env("GOOGLE_CLIENT_SECRET", default=""),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
    }
}
