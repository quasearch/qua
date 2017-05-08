import os

from qua import constants
from qua import settings as qua_settings


APP_NAME = qua_settings.PROGRAM_NAME + '.suggests'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'somestrongdjangokey'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'rest_framework',
    'django_rq',
    'suggests.apps.SuggestsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'qua.rest.middleware.LoggingMiddleware'
]

if DEBUG:
    DATABASE_HOST = '127.0.0.1'
else:
    DATABASE_HOST = qua_settings.POSTGRESQL['host']

DATABASES = {
    'default': {
        'ENGINE': qua_settings.POSTGRESQL['engine'],
        'NAME': APP_NAME.replace('.', '_'),
        'HOST': DATABASE_HOST,
        'PORT': qua_settings.POSTGRESQL['port'],
        'USER': qua_settings.POSTGRESQL['user'],
        'PASSWORD': qua_settings.POSTGRESQL['password']
    }
}

ROOT_URLCONF = 'app.urls'

WSGI_APPLICATION = 'app.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'qua.rest.exceptions.api_exception_handler',
}

RQ_QUEUES = {
    APP_NAME: {
        'HOST': qua_settings.REDIS['host'],
        'PORT': qua_settings.REDIS['port'],
        'DB': qua_settings.REDIS['db_cache']
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(filename)s:'
                      '%(funcName)s:%(lineno)s '
                      '%(levelname)s: %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(message)s'
        },
    },
    'handlers': {
        'qua': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(qua_settings.LOGS_DIR, APP_NAME + '.log'),
            'formatter': 'verbose'
        },
        'requests': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(
                qua_settings.LOGS_DIR, APP_NAME + '.requests.log'),
            'formatter': 'simple'
        }
    },
    'loggers': {
        'qua': {
            'handlers': ['qua'],
            'level': 'DEBUG',
            'propagate': True
        },
        'qua.requests': {
            'handlers': ['requests'],
            'level': 'INFO',
            'propagate': False
        }
    },
}

SUGGEST_PREPROCESSOR = {
    'max_last': 100,     # How old user history queries will be used (days)
    'min_query_len': 2,  # Minimal query len will be used in suggests
    'replacements': [    # What letters will be replaces
        ('ё', 'е')       # while preprocessing suggests data
    ]
}

# How many suggests will be returned by default
SUGGESTS_DEFAULT_LIMIT = 10

# Tree file properties
SUGGESTS_TREE_PREFIX = APP_NAME + '.suggests_tree'

SUGGESTS_TREE_PATH = os.path.join(qua_settings.DATA_DIR, SUGGESTS_TREE_PREFIX)

# Check new data and recreate tree every such interval
SUGGESTS_UPDATE_INTERVAL = 2 * constants.MINUTE

# Property for request handler. Every `n` query check updates in tree file
SUGGESTS_REQUEST_UPDATE_INTERVAL = 1000