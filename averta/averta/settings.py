from dotenv import load_dotenv
from pathlib import Path
import os
import sys

load_dotenv('')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# --- Cloudflare Turnstile (Captcha) ---
# Checkbox widget uses `cf-turnstile-response` POST field.
TURNSTILE_SITE_KEY = (os.getenv('TURNSTILE_SITE_KEY') or '').strip()
TURNSTILE_SECRET_KEY = (os.getenv('TURNSTILE_SECRET_KEY') or '').strip()

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv('ALLOWED_HOSTS', 'avertatravel.com,www.avertatravel.com,localhost,127.0.0.1').split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    'https://avertatravel.com',
    'https://www.avertatravel.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

_extra_csrf = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend(
        o.strip() for o in _extra_csrf.split(',') if o.strip()
    )


# Admin URL - secret path (required)
ADMIN_URL = os.getenv('ADMIN_URL')
if not ADMIN_URL:
    # Allow management commands (e.g. makemessages) to run locally
    # even when env vars are not configured.
    if any(cmd in sys.argv for cmd in ('makemessages', 'compilemessages', 'check', 'test', 'collectstatic', 'migrate', 'createsuperuser')):
        ADMIN_URL = 'admin/'
    else:
        raise ValueError("ADMIN_URL environment variable is required!")
if not ADMIN_URL.endswith('/'):
    ADMIN_URL += '/'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Packages
    'django_cleanup.apps.CleanupConfig',
    'ckeditor',
    
    # Apps
    'services.apps.ServicesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'averta.middleware.CsrfNullOriginFixMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'averta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'services.context_processors.navbar_services',
                'services.context_processors.site_contact',
                'services.context_processors.turnstile',
            ],
        },
    },
]


WSGI_APPLICATION = 'averta.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}


# Cache configuration
# https://docs.djangoproject.com/en/5.2/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'averta-cache',
        'TIMEOUT': 7200,  # 2 hours default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Cache timeout settings (in seconds)
CACHE_TIMEOUT_SHORT = 1800  # 30 minutes for occasionally changing data
CACHE_TIMEOUT_MEDIUM = 7200  # 2 hours for normal pages (services, blog lists)
CACHE_TIMEOUT_LONG = 86400  # 24 hours for stable data (about, contact, background images)

# Bump when serialized cache payload shape changes (e.g. new Package.currency field).
CACHE_SCHEMA_VERSION = 3


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


LANGUAGE_CODE = 'az'
ADMIN_LANGUAGE_CODE = 'az'

LANGUAGES = [
    ('az', 'Azərbaycan'),
    ('en', 'English'),
    ('ru', 'Русский'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Asia/Baku'

USE_I18N = True

USE_TZ = True

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
# Media / Static configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files directories
STATICFILES_DIRS = [
    os.path.join(str(BASE_DIR), 'static'),
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
from .ckeditor_presets import CKEDITOR_PROJECT_CONFIG

CKEDITOR_CONFIGS = CKEDITOR_PROJECT_CONFIG


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
CONTACT_RECEIVER_EMAIL = os.getenv('CONTACT_RECEIVER_EMAIL', EMAIL_HOST_USER)
SITE_NAME = os.getenv('SITE_NAME', 'Averta.az')

# Allow local overrides without changing DJANGO_SETTINGS_MODULE
try:
    from .settings_local import *  # noqa: F403,F401
except Exception:
    pass
