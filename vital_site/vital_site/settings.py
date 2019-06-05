"""
Django settings for vital_site project.
"""

import os
import configparser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = configparser.ConfigParser()

# this is the original!
#config.read("/home/vital/config.ini")

# here's the new
config.read("config.ini")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get("Security", "SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
ADMINS = config.get("Email", "VITAL_ADMINS")

# Application definition

INSTALLED_APPS = [
    'vital.apps.VitalConfig',
    'captcha',
    'passwords',
    'session_security',
    'jquery',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# this was added as per https://code.djangoproject.com/ticket/30237
MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'vital_site.urls'

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

WSGI_APPLICATION = 'vital_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

# FIXME - original below, must adde flag for using SQLite in 'dev mode'
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': config.get("Database", "VITAL_DB_NAME"),
#         'USER': config.get("Database", "VITAL_DB_USER"),
#         'PASSWORD': config.get("Database", "VITAL_DB_PWD"),
#         'HOST': config.get("Database", "VITAL_DB_HOST"),
#         'PORT': config.get("Database", "VITAL_DB_PORT"),
#     }
# }

# TODO - make flag to launch this configuration
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

AUTH_USER_MODEL = 'vital.VLAB_User'
#AUTHENTICATION_BACKENDS = ['vital.backends.EmailAuthBackend', ]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/home/vital/vital_static'

CAPTCHA_IMAGE_SIZE = (120, 50)
CAPTCHA_FONT_SIZE = 32
CAPTCHA_OUTPUT_FORMAT = u'%(image)s %(hidden_field)s <br> %(text_field)s'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            # original - changed for Python 3
            #'filename': '/var/log/vital/vital.log',
            'filename': 'vital.log',
            'maxBytes': 1024*1024*1, # 1 MB
            'backupCount': 15,
            'formatter': 'verbose'
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'vital': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = config.get("Email", "VITAL_EMAIL_HOST")
EMAIL_HOST_USER = config.get("Email", "VITAL_EMAIL_USER")
EMAIL_HOST_PASSWORD = config.get("Email", "VITAL_EMAIL_PWD")
EMAIL_PORT = config.get("Email", "VITAL_EMAIL_PORT")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Email Host for Error Reporting
SERVER_EMAIL = EMAIL_HOST

PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = {"UPPER":  1, "LOWER":  1, "DIGITS": 1}

SESSION_COOKIE_AGE = 10800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_WARN_AFTER = 9000
SESSION_SECURITY_EXPIRE_AFTER = SESSION_COOKIE_AGE
