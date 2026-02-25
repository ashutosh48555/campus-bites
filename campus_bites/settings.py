from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if host]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "shops",
    "menu",
    "orders",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]

ROOT_URLCONF = "campus_bites.urls"

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
                "accounts.context_processors.notification_count",
            ],
        },
    }
]

WSGI_APPLICATION = "campus_bites.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # For production deployment
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user uploads)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===== AUTHENTICATION & AUTHORIZATION SETTINGS =====

# Login/Logout URLs
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "shops:list"
LOGOUT_REDIRECT_URL = "shops:list"

# Session Security
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SECURE = not DEBUG  # Use HTTPS in production
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep session after browser close

# CSRF Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG  # Use HTTPS in production
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Password Validation - Enhanced
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,  # Minimum 8 characters
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True  # X-XSS-Protection header
SECURE_CONTENT_TYPE_NOSNIFF = True  # X-Content-Type-Options header
X_FRAME_OPTIONS = 'DENY'  # Clickjacking protection

# Production Security Settings (Enable when DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Email Configuration for Password Reset
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development: prints to console
# For production, use SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@shopapp.com')

# Login Attempt Limits
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5  # Custom setting
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes lockout

# Password Reset Token Validity
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour (in seconds)

