"""
Django settings for cjworkbench project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import sys
from os.path import abspath, basename, dirname, join, normpath
from server.utils import user_display

if sys.version_info[0] < 3:
    raise RuntimeError('CJ Workbench requires Python 3')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration below uses these instead of BASE_DIR
DJANGO_ROOT = dirname(dirname(abspath(__file__)))
SITE_ROOT = dirname(DJANGO_ROOT)
SITE_NAME = basename(DJANGO_ROOT)
SITE_ID = 1
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
if 'CJW_PRODUCTION' in os.environ:
    DEBUG = not os.environ['CJW_PRODUCTION']
else:
    DEBUG=True

DEFAULT_FROM_EMAIL = 'Workbench <hello@accounts.cjworkbench.org>'

# Various environment variables must be set in production
if DEBUG==False:
    try:
        SECRET_KEY = os.environ['CJW_SECRET_KEY']
    except KeyError:
        sys.exit('Must set CJW_SECRET_KEY in production')

    if 'CJW_DB_HOST' not in os.environ:
        sys.exit('Must set CJW_DB_HOST in production')

    if 'CJW_DB_PASSWORD' not in os.environ:
        sys.exit('Must set CJW_DB_PASSWORD in production')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'cjworkbench',
            'USER': 'cjworkbench',
            'HOST': os.environ['CJW_DB_HOST'],
            'PASSWORD': os.environ['CJW_DB_PASSWORD'],
            'PORT': '5432',
        }
    }

    if 'CJW_SENDGRID_API_KEY' not in os.environ:
        sys.exit('Must set CJW_SENDGRID_API_KEY in production')

    if not all(x in os.environ for x in [
        'CJW_SENDGRID_INVITATION_ID',
        'CJW_SENDGRID_CONFIRMATION_ID',
        'CJW_SENDGRID_PASSWORD_CHANGE_ID',
        'CJW_SENDGRID_PASSWORD_RESET_ID'
        ]):
        sys.exit('Must set Sendgrid template IDs for all system emails')

    EMAIL_BACKEND = 'sgbackend.SendGridBackend'
    SENDGRID_API_KEY = os.environ['CJW_SENDGRID_API_KEY']
    ACCOUNT_HOOKSET = "cjworkbench.sendgrid_email.SendgridEmails"
    SENDGRID_TEMPLATE_IDS = {
        'invitation': os.environ['CJW_SENDGRID_INVITATION_ID'],
        'confirmation': os.environ['CJW_SENDGRID_CONFIRMATION_ID'],
        'password_change': os.environ['CJW_SENDGRID_PASSWORD_CHANGE_ID'],
        'password_reset': os.environ['CJW_SENDGRID_PASSWORD_RESET_ID'],
    }

else:
    # We are running in debug
    SECRET_KEY = 'my debug secret key is not a secret'

    # Database
    # https://docs.djangoproject.com/en/1.10/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'local_mail')

if 'CJW_GOOGLE_ANALYTICS' in os.environ:
    GOOGLE_ANALYTICS_PROPERTY_ID = os.environ['CJW_GOOGLE_ANALYTICS']

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'cjworkbench',
    'server.apps.ServerConfig',
    'webpack_loader',
    'rest_framework',
    'channels',
    'account',
    'polymorphic',
    'analytical'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'account.middleware.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'cjworkbench.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.account',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

WSGI_APPLICATION = 'cjworkbench.wsgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgiref.inmemory.ChannelLayer',
        'ROUTING': 'cjworkbench.routing.channel_routing',
    },
}




# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

LOGIN_URL = '/account/login'
LOGIN_REDIRECT_URL = '/workflows'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# I don't think we actually use this, we're webpack instead -- jms 2017-7-24

STATIC_URL = '/static/'
STATIC_ROOT = normpath(join(DJANGO_ROOT, 'static'))
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'), # We do this so that django's collectstatic copies or our bundles to the STATIC_ROOT or syncs them to whatever storage we use.
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Webpack loads all our js/css into handy bundles
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

# Redirect logs to console on prod, so we can view them with docker logs
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# User accounts

ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_USER_DISPLAY = user_display

AUTHENTICATION_BACKENDS = [
    'account.auth_backends.EmailAuthenticationBackend',
]

GOOGLE_OAUTH2_CLIENT_SECRETS_JSON = os.path.join(BASE_DIR, os.environ['CJW_GOOGLE_CLIENT_SECRETS'])

try:
    from local_settings import *
except ImportError:
    pass
