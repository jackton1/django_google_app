"""
Django settings for eval_project project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import json
import os
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+#z9@$brqm+z*@4me@wrl9ud)rjcqz7s-m+q#gm$pgpd#g%s^s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

PROJECT_APPS = ['easy_maps',
                'map_app',
                'django_tables2',
                # 'compressor',
                # 'compressor_toolkit',
                'static_precompiler',
                'oauth2client',
                'googleapiclient',
                'geopy',
                ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap_breadcrumbs',
] + PROJECT_APPS

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eval_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eval_project.wsgi.application'

# Breadcrumb template
BREADCRUMBS_TEMPLATE = 'django_bootstrap_breadcrumbs/bootstrap3.html'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

# Update the messages error tag for bootstrap
MESSAGES_TAGS = {messages.ERROR: 'danger'}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join('public', 'static')

# Allow collectstatic find the precompiled files.
STATIC_PRECOMPILER_FINDER_LIST_FILES = False

# Folder to store the compiled files using the STATIC_ROOT
STATIC_PRECOMPILER_OUTPUT_DIR = 'compiled'

GOOGLE_API_KEYS_JSON_FILE = os.path.join(BASE_DIR, 'google_api_keys.json')

EASY_MAPS_GOOGLE_MAPS_API_KEY = json.load(open(GOOGLE_API_KEYS_JSON_FILE),
                                          object_hook=lambda f: f['maps-api-key'])

GOOGLE_FUSION_TABLE_API_KEY = json.load(open(GOOGLE_API_KEYS_JSON_FILE),
                                        object_hook=lambda f: f['fusion-table-api-key'])

SECRET = json.load(open(GOOGLE_API_KEYS_JSON_FILE),
                   object_hook=lambda f: f['client-secret'])

VIEW_GOOGLE_MAP_LINK = 'https://www.google.com/maps/search/?api=1&map_action=map'

GOOGLE_OAUTH2_CLIENT_SECRETS_JSON = os.path.join(BASE_DIR, 'client_id.json')

GOOGLE_SERVICE_ACCOUNT_KEY_FILE = os.path.join(BASE_DIR, 'service_account.json')

FUSION_TABLE_SCOPE = 'https://www.googleapis.com/auth/fusiontables'

OAUTH2_CLIENT_REDIRECT_PATH = 'http://localhost:8000/oauth2callback'

FUSION_TABLE_ID = '1ckNKTPf6djI8teuiQuxExAQwMXSqytwvAWdh7yAQ'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'map_app', 'static'),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'static_precompiler.finders.StaticPrecompilerFinder',
)

STATIC_EXCLUDE_APPS = (
    'django.contrib.admin',
    'django_tables2',
)

STATIC_PRECOMPILER_COMPILERS = (
    ('static_precompiler.compilers.Babel',
        {"executable": os.path.join('node_modules', '.bin', 'babel'),
         "sourcemap_enabled": True}
    ),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s %(thread)d %(name)s %(pathname)s] %(levelname)s : %(message)s',
            'datefmt': '%a, %d/%b/%Y %H:%M:%S'
        },
        'simple': {
            'format': '[%(asctime)s %(module)s] %(levelname)s : %(message)s',
            'datefmt': '%a, %d/%b/%Y  %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': ('simple' if not DEBUG else 'verbose')
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True
        },
        'map_app': {
            'handlers': ['console'],
            'level': ('DEBUG' if DEBUG else 'INFO')
        },
        'easy_maps': {
            'handlers': ['console'],
            'level': ('DEBUG' if DEBUG else 'INFO')
        }
    },
}
