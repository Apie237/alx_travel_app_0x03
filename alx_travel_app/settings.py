
import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_extensions',
    
    # Local apps
    'listings',
    'bookings',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alx_travel_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'alx_travel_app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Celery task configuration
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery task execution settings
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard time limit
CELERY_TASK_SOFT_TIME_LIMIT = 5 * 60  # 5 minutes soft time limit
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Celery beat configuration for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-bookings': {
        'task': 'listings.tasks.cleanup_expired_bookings',
        'schedule': 3600.0,  # Run every hour
    },
}

# Celery task routing
CELERY_TASK_ROUTES = {
    'listings.tasks.send_booking_confirmation_email': {'queue': 'emails'},
    'listings.tasks.send_booking_reminder_email': {'queue': 'emails'},
    'listings.tasks.cleanup_expired_bookings': {'queue': 'cleanup'},
}

# Celery task annotations for rate limiting
CELERY_TASK_ANNOTATIONS = {
    'listings.tasks.send_booking_confirmation_email': {
        'rate_limit': '50/m',  # 50 emails per minute
        'max_retries': 3,
        'default_retry_delay': 60,
    },
    'listings.tasks.send_booking_reminder_email': {
        'rate_limit': '30/m',  # 30 reminder emails per minute
        'max_retries': 3,
        'default_retry_delay': 60,
    },
}

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@alxtravel.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Email timeout settings
EMAIL_TIMEOUT = 30

# Application-specific settings
SITE_NAME = config('SITE_NAME', default='ALX Travel App')
SITE_URL = config('SITE_URL', default='http://localhost:8000')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@alxtravel.com')

# Booking settings
BOOKING_CONFIRMATION_EMAIL_ENABLED = config('BOOKING_CONFIRMATION_EMAIL_ENABLED', default=True, cast=bool)
BOOKING_REMINDER_HOURS_BEFORE = config('BOOKING_REMINDER_HOURS_BEFORE', default=24, cast=int)
MAX_BOOKING_DAYS_AHEAD = config('MAX_BOOKING_DAYS_AHEAD', default=365, cast=int)

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session configuration
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'celery': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'celery.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'celery': {
            'handlers': ['console', 'celery'],
            'level': config('CELERY_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'listings.tasks': {
            'handlers': ['console', 'celery'],
            'level': 'INFO',
            'propagate': False,
        },
        'bookings': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(exist_ok=True)

# Cache configuration (for production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('CACHE_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'alx_travel_app',
        'VERSION': 1,
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}

# Internationalization and localization
USE_L10N = True
DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = ','

# Custom user model (if needed in future)
# AUTH_USER_MODEL = 'accounts.User'

# API versioning
API_VERSION = 'v1'

# Development settings
if DEBUG:
    # Django Debug Toolbar (optional)
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
    except ImportError:
        pass
    
    # Disable cache in development
    CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

# Testing settings
if 'test' in os.sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    
    # Use in-memory cache for testing
    CACHES['default']['BACKEND'] = 'django.core.cache.backends.locmem.LocMemCache'
    
    # Disable migrations during tests
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    
    MIGRATION_MODULES = DisableMigrations()
    
    # Use console email backend for tests
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    # Disable Celery in tests
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True