# Django settings for camera archive project.

import sys
from pathlib import Path

# turn warnings into exception...
# import warnings
# warnings.filterwarnings(
#     'error', r"DateTimeField .* received a naive datetime",
#     RuntimeWarning, r'django\.db\.models\.fields')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.contrib import messages

BASE_DIR = Path(Path(Path(__file__).resolve()).parent).parent
PROJECT_APP_PATH = Path(Path(__file__).resolve()).parent
PROJECT_APP = Path(PROJECT_APP_PATH).name

# Settings for tests, override in production with localsettings!
DEBUG = True

SECRET_KEY = 'django-insecure-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'  # noqa: S105

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': Path(BASE_DIR) / 'cam_archive.db',  # Or path to database file if using sqlite3.
    },
}

ADMINS = [
    ('cwiegand', 'cwiegand@wgdnet.de'),
]

MANAGERS = ADMINS

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de'
# LANGUAGE_CODE = 'en-US'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'

STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR) / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(BASE_DIR) / 'media'

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'account_login'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'cam_archive.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'cam_archive.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'cam_archive',
    'allauth',
    'allauth.account',
    'allauth.mfa',
    'video',
    'camera',
    'django_filters',
    'dark_mode_switch',
    'django_bootstrap_icons',
    'django_bootstrap5',
]

ACCOUNT_ACTIVATION_DAYS = 3

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

BOOTSTRAP5 = {
    # 'theme_url': '/static/css/bootstrap.min.css',
}

# All-auth settings
ACCOUNT_LOGIN_METHODS = {"username"}
MFA_PASSKEY_LOGIN_ENABLED = True

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# disable axes if debug True
AXES_ENABLED = not DEBUG

# Ring api token
API_TOKEN = '&ft9o6r+9rc8l%&u#!3n(d&&g(f^fg74y)^d#(fx0i+@as-atf'  # noqa: S105

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing "from .local_settings import *", we use exec so that
# local_settings has full access to everything defined in this module.
# Also force into sys.modules so it's visible to Django's autoreload.

f = Path(PROJECT_APP_PATH) / "localsettings.py"
if Path.exists(f):
    import importlib
    module_name = f"{PROJECT_APP}.localsettings"
    module = importlib.import_module(module_name)
    module.__file__ = f
    sys.modules[module_name] = module
    with Path.open(f, "rb") as settings_file:
        exec(settings_file.read())  # noqa: S102
