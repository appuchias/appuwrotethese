# Appu Wrote These
# Copyright (C) 2023  Appuchia <appuchia@appu.ltd>


import logging
from pathlib import Path
from secrets import token_urlsafe

from django.contrib import messages
from django.utils.translation import gettext_lazy as _


DEBUG = False


with open("settings.conf", "r") as f:
    config = {k: v.strip() for k, v in [line.split("=") for line in f.readlines()]}

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config.get("SECRET_KEY")
if SECRET_KEY is None:
    SECRET_KEY = token_urlsafe(64)
    logging.warning(
        "settings: SECRET_KEY was not set. New one generated for this session. Please set it as an environment variable or in `config.yaml`."
    )
# SECRET_KEY_FALLBACKS = config.get("SECRET_KEY_FALLBACKS", [])

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost",
]

ROOT_URLCONF = "appuwrotethese.urls"

ALLOWED_HOSTS = [
    "appu.ltd",
    "www.appu.ltd",
    "*" if DEBUG else None,
]

ADMINS = [("Appu", "appuchia@appu.ltd")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_user_agents",
    "crispy_forms",
    "crispy_bootstrap5",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "gas",
    "accounts",
    "mastermind",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "middleware.persistent_messages_middleware.PersistentMessagesMiddleware",
]

COMPRESS_ENABLED = True


LOGFILE_NAME = r"log/appuwrotethese"
LOGFILE_SIZE = 50 * 1024 * 1024  # 50 MB
LOGFILE_COUNT = 2
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "logfile": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGFILE_NAME + ".log",
            "maxBytes": LOGFILE_SIZE,
            "backupCount": LOGFILE_COUNT,
            "formatter": "standard",
            "delay": True,
        },
        "logfile_debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGFILE_NAME + "_debug.log",
            "filters": ["require_debug_true"],
            "maxBytes": LOGFILE_SIZE,
            "backupCount": LOGFILE_COUNT,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["logfile", "logfile_debug"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


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

WSGI_APPLICATION = "appuwrotethese.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Authentication
LOGIN_URL = "/accounts/login/"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Language and i18n
LANGUAGE_CODE = "en-us"
USE_I18N = True
LANGUAGES = [
    ("es", _("Spanish")),
    ("en", _("English")),
]
LANGUAGE_COOKIE_NAME = "lang"
LOCALE_PATHS = (BASE_DIR / "locale",)
FIRST_DAY_OF_WEEK = 1

USE_TZ = True
TIME_ZONE = "Europe/Madrid"

# Staticfiles
STATIC_URL = "/s/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_URL = "/m/"

# User agents
USER_AGENTS_CACHE = "default"

# Django crispy forms template
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email setup
EMAIL_HOST = "in-v3.mailjet.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = config.get("SMTP_USER", "")
EMAIL_HOST_PASSWORD = config.get("SMTP_PASS", "")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
SERVER_EMAIL = "noreply@appu.ltd"

# Messages setup
MESSAGE_LEVEL = messages.DEBUG if DEBUG else messages.INFO
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
MESSAGE_TAGS = {
    messages.DEBUG: "primary",
    messages.INFO: "secondary",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}
