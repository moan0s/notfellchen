"""
Django settings for notfellchen project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import configparser
from django.utils.translation import gettext_lazy as _
from celery import Celery

"""CONFIG PARSER """
config = configparser.RawConfigParser()
if 'NF_CONFIG_FILE' in os.environ:
    config.read_file(open(os.environ.get('NF_CONFIG_FILE'), encoding='utf-8'))
if 'DOCKER_BUILD' in os.environ and os.environ.get('DOCKER_BUILD'):
    config.read("docker/build.cfg", encoding='utf-8')
else:
    config.read(['/etc/notfellchen/notfellchen.cfg', os.path.expanduser('~/.notfellchen.cfg'), 'notfellchen.cfg'],
                encoding='utf-8')

CONFIG_FILE = config

DJANGO_LOG_LEVEL = config.get('logging', 'django_log_level', fallback="WARNING")
APP_LOG_LEVEL = config.get('logging', 'app_log_level', fallback="WARNING")

"""LOGGING"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
        },
        'fellchensammlung': {
            'handlers': ['console'],
            'level': APP_LOG_LEVEL,
        },
        'notfellchen': {
            'handlers': ['console'],
            'level': APP_LOG_LEVEL,
        },
    },
}

""" DJANGO """
try:
    SECRET_KEY = config.get('django', 'secret')
except configparser.NoSectionError:
    raise BaseException("No config found or no Django Secret is configured!")
DEBUG = config.getboolean('django', 'debug', fallback=False)

""" DATABASE """
DB_BACKEND = config.get("database", "backend", fallback="sqlite3")
DB_NAME = config.get("database", "name", fallback="notfellchen.sqlite3")
DB_USER = config.get("database", "user", fallback='')
DB_PASSWORD = config.get("database", "password", fallback='')
DB_HOST = config.get("database", "host", fallback='')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

""" CELERY + KEYDB """
CELERY_BROKER_URL = config.get("celery", "broker", fallback="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config.get("celery", "backend", fallback="redis://localhost:6379/0")

""" MONITORING """
HEALTHCHECKS_URL = config.get("monitoring", "healthchecks_url", fallback=None)

""" GEOCODING """
GEOCODING_API_URL = config.get("geocoding", "api_url", fallback="https://nominatim.hyteck.de/search")
# GEOCODING_API_FORMAT is allowed to be one of ['nominatim', 'photon']
GEOCODING_API_FORMAT = config.get("geocoding", "api_format", fallback="nominatim")

""" Tile Server """
MAP_TILE_SERVER = config.get("map", "tile_server", fallback="https://tiles.hyteck.de")

""" OxiTraffic"""
OXITRAFFIC_ENABLED = config.get("tracking", "oxitraffic_enabled", fallback=False)
OXITRAFFIC_BASE_URL = config.get("tracking", "oxitraffic_base_url", fallback="")

""" E-MAIL  """
console_only = config.getboolean("mail", "console_only", fallback="true")
EMAIL_SUBJECT_PREFIX = config.get("mail", "prefix", fallback="[notfellchen]]")
if console_only:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_HOST = config.get('mail', 'host', fallback='localhost')
    EMAIL_PORT = config.getint('mail', 'port', fallback=25)
    EMAIL_HOST_USER = config.get('mail', 'user', fallback='')
    DEFAULT_FROM_EMAIL = config.get('mail', 'from', fallback='notfellchen@localhost')
    EMAIL_HOST_PASSWORD = config.get('mail', 'password', fallback='')
    EMAIL_USE_TLS = config.getboolean('mail', 'tls', fallback=False)
    EMAIL_USE_SSL = config.getboolean('mail', 'ssl', fallback=False)

"""USER MANAGEMENT"""
AUTH_USER_MODEL = "fellchensammlung.User"
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
REGISTRATION_OPEN = True
REGISTRATION_SALT = "notfellchen"

""" SECURITY.TXT """
SEC_CONTACT = config.get("security", "Contact", fallback="julian-samuel@gebuehr.net")
SEC_EXPIRES = config.get("security", "Expires", fallback="2028-03-17T07:00:00.000Z")
SEC_ENCRYPTION = config.get("security", "Encryption", fallback="https://hyteck.de/julian-samuel@gebuehr.net.pub.asc")
SEC_LANG = config.get("security", "Preferred-Languages", fallback="en, de")
SEC_SCOPE = config.get("security", "Scope",
                       fallback="The provided contact is the main developer of the application and NOT necessarily the "
                                "instance")
SEC_POLICY = config.get("security", "Policy",
                        fallback="Do NOT include user data or detailed reports (especially public or unencrypted) "
                                 "without being asked to do so.")

""" LOCATIONS """
STATIC_ROOT = config.get("locations", "static", fallback="/notfellchen/static")
MEDIA_ROOT = config.get("locations", "media", fallback="/notfellchen/static")
MEDIA_URL = config.get("urls", "media", fallback="/media/")

host = config.get("notfellchen", "host", fallback='*')

# see https://docs.djangoproject.com/en/3.2/ref/settings/#std-setting-ALLOWED_HOSTS
ALLOWED_HOSTS = [host]
CSRF_TRUSTED_ORIGINS = [f"https://{host}"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# This is adjusted based on this guide https://testdriven.io/blog/django-docker-traefik/
# compression and caching support (see https://whitenoise.readthedocs.io/en/latest/#quickstart-for-django-apps)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATIC_URL = '/static/'

"""Application definition"""

INSTALLED_APPS = [
    'fellchensammlung',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.sitemaps",
    'fontawesomefree',
    'crispy_forms',
    "crispy_bootstrap4",
    "rest_framework",
    'rest_framework.authtoken',
    'drf_spectacular',
    'drf_spectacular_sidecar',  # required for Django collectstatic discovery
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Static file serving & caching
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Needs to be after SessionMiddleware and before CommonMiddleware
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'notfellchen.urls'

SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'notfellchen.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if (DB_BACKEND == "sqlite3"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DB_NAME,
        }
    }
elif (DB_BACKEND == "postgresql"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
        }
    }
else:
    print("Database backend unknown. Choose sqlite3 or postgresql")

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = config.get('locale', 'default', fallback='de')
LANGUAGE_COOKIE_NAME = "selected-language"
TIME_ZONE = config.get('locale', 'timezone', fallback='UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('de', _('German')),
)

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'TITLE': 'Notfellchen API',
    'DESCRIPTION': 'Adopt a animal in need',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
