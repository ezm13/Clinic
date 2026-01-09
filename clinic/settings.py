# clinic/settings.py

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# CORE
# =========================
SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_SUPER_SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".up.railway.app",     # ✅ permite subdominios de Railway
]

# Si tienes un dominio propio, agrégalo aquí, por ejemplo:
# ALLOWED_HOSTS += ["tudominio.com"]

# Para CSRF en producción (Railway)
CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
]
# Si usas dominio propio:
# CSRF_TRUSTED_ORIGINS += ["https://tudominio.com"]

# Proxy headers (Railway / reverse proxy)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# =========================
# APPS
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Tus apps
    "accounts",
    "appointments",
    "patients",
    "prescriptions",
    "notes",
    "records",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # ✅ WhiteNoise para servir static en Railway
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "clinic.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # ✅ tu carpeta templates/
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "clinic.wsgi.application"


# =========================
# DATABASE (SQLite local / Postgres Railway)
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # ✅ Railway: Postgres
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,  # ✅ aquí sí aplica (Postgres)
        )
    }
else:
    # ✅ Local: SQLite (sin sslmode)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================
# PASSWORDS
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =========================
# I18N / TIME
# =========================
LANGUAGE_CODE = "es-cr"
TIME_ZONE = "America/Costa_Rica"
USE_I18N = True
USE_TZ = True


# =========================
# STATIC / MEDIA
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # ✅ donde collectstatic genera todo
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================
# AUTH (opcional)
# =========================
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# =========================
# DEFAULTS
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
