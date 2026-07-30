"""
Paramètres Django du projet "Plateforme de Gestion de Tâches".

Ce fichier est conçu pour fonctionner à la fois :
- en local (DEBUG=True, base SQLite)
- en production sur Railway (DEBUG=False, PostgreSQL via DATABASE_URL)

Toutes les valeurs sensibles sont lues depuis des variables d'environnement
(fichier .env en local, "Variables" Railway en production).
"""

from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sécurité -------------------------------------------------------------

SECRET_KEY = config("SECRET_KEY", default="django-insecure-changeme-en-local-uniquement")

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Applications -----------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "projects",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# En local (DEBUG=True) : stockage simple, aucune étape supplémentaire requise,
# `runserver` sert les fichiers statiques directement.
# En production (DEBUG=False) : stockage compressé + "manifeste" (noms de
# fichiers avec hash, pour un cache navigateur fiable), qui EXIGE d'avoir
# lancé `python manage.py collectstatic` avant de démarrer le serveur.
# C'est pourquoi le Procfile et le pipeline CI exécutent tous les deux
# `collectstatic` avant de lancer respectivement Gunicorn et les tests.
STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:connexion"
LOGIN_REDIRECT_URL = "projects:liste_projets"
LOGOUT_REDIRECT_URL = "accounts:connexion"

if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- E-mail (utilisé par "Mot de passe oublié") ------------------------------
#
# En local (DEBUG=True par défaut) : les e-mails sont simplement affichés dans
# le terminal où tourne `runserver`, aucune configuration n'est nécessaire.
#
# En production : définissez EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
# (par exemple avec un compte Gmail "mot de passe d'application", SendGrid,
# Mailgun...) dans les variables d'environnement pour envoyer de vrais e-mails.

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend" if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@gestion-taches.local")

# Durée de validité d'un lien de réinitialisation de mot de passe (en secondes).
# 86400 = 24 heures.
PASSWORD_RESET_TIMEOUT = 86400
