"""
Django settings for travelbear project.

Generated by "django-admin startproject" using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import logging
import os

logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ["*"]
ALLOWED_ENVIRONMENTS = ["production", "staging", "development", "test"]


ENVIRONMENT = None
DJANGO_LOG_LEVEL = "INFO"
SECRET_KEY = "dev.secret.key"
AUTH_API_AUDIENCE = ""
AUTH_PUBLIC_KEY_PATH = ""

DB_NAME = None
DB_USER = None
DB_PASSWORD = None
DB_HOST = None

TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
TWILIO_MESSAGING_SERVICE_SID = None


SETTINGS_FROM_ENVIRONMENT = (
    "DJANGO_LOG_LEVEL",

    "ENVIRONMENT",
    "SECRET_KEY",
    "AUTH_API_AUDIENCE",

    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",

    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_MESSAGING_SERVICE_SID",
)

for setting_name in SETTINGS_FROM_ENVIRONMENT:
    env_value = os.getenv(setting_name)
    if env_value is not None:
        vars()[setting_name] = env_value


for setting_name in SETTINGS_FROM_ENVIRONMENT:
    if vars()[setting_name] is None:
        logger.warning(f"Missing setting {setting_name}: set with environment variable")


if ENVIRONMENT not in ALLOWED_ENVIRONMENTS:
    allowed_environments_string = ", ".join(ALLOWED_ENVIRONMENTS)
    raise EnvironmentError(
        f"invalid ENVIRONMENT {ENVIRONMENT}: must be one of {allowed_environments_string}"
    )


IS_PROD_ENVIRONMENT = ENVIRONMENT == "production"
IS_STAGING_ENVIRONMENT = ENVIRONMENT == "staging"
IS_DEV_ENVIRONMENT = ENVIRONMENT == "development"
IS_TEST_ENVIRONMENT = ENVIRONMENT == "test"

DEBUG = IS_DEV_ENVIRONMENT


# Application definition

PROJECT_APPS = ["db_layer"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
] + PROJECT_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_conf.urls"

APPEND_SLASH = False

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
            ]
        },
    }
]

WSGI_APPLICATION = "django_conf.wsgi.application"


# Logging
# https://docs.djangoproject.com/en/2.1/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": True,
        },
    },
}


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": 5432,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"


# CORS
# https://pypi.org/project/django-cors-headers/

# TODO: Change this to use frontend url once we know what it is
CORS_ORIGIN_ALLOW_ALL = True
