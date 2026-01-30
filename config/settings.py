from pathlib import Path
import os  # MOD: Afegit per poder usar rutes/variables entorn

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-y$1u2*vp6rs)=3^$yl#4)&6y1k7nx0f!3pfir4_d3n=1r3)1%w'  # MOD: En producció usar variable d'entorn
DEBUG = True  # MOD: Posar False en producció
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # MOD: Afegits hosts locals (evita errors en execució)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',  # MOD: App d'usuari personalitzada
    'events',
    'chat',
    'semantic_search',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # MOD: Carpeta global de plantilles
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

WSGI_APPLICATION = 'config.wsgi.application'

# MOD: Canvi de base de dades (sqlite -> MongoDB via djongo)
DATABASES = {
    'default': {  # MOD
        'ENGINE': 'djongo',  # MOD: Motor djongo
        'NAME': 'streamevents_db',  # MOD: Nom BBDD
        'ENFORCE_SCHEMA': False,  # MOD: Validació d'esquema
        'CLIENT': {  # MOD
            'host': 'mongodb://localhost:27017'  # MOD: Connexió Mongo
        }  # MOD
    }  # MOD
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ca'  # MOD: Canvi d'en-us a català
TIME_ZONE = 'Europe/Madrid'  # MOD: Canvi d'UTC a zona local
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'  # MOD: Afegit slash inicial per consistència
# STATICFILES_DIRS = [BASE_DIR / 'static']  # MOD (opcional si tens carpeta pròpia)
# STATIC_ROOT = BASE_DIR / 'staticfiles'  # MOD (per desplegament)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_URL = '/media/'  # MOD: Suport fitxers pujats
MEDIA_ROOT = BASE_DIR / 'media'  # MOD: Directori media

AUTH_USER_MODEL = 'users.CustomUser'  # MOD: Model d'usuari personalitzat (definir abans primer migrate)

LOGIN_URL = 'users:login'  # MOD: Nom URL login
LOGIN_REDIRECT_URL = 'home'  # MOD: Destí després d'iniciar sessió
LOGOUT_REDIRECT_URL = 'login'  # MOD: Destí després de tancar sessió

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from django.contrib.messages import constants as messages  # MOD: Per personalitzar etiquetes missatges
MESSAGE_TAGS = {  # MOD: Adaptació a classes Bootstrap
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# (Opcional futur producció)
# CSRF_COOKIE_SECURE = True  # MOD
# SESSION_COOKIE_SECURE = True  # MOD
# SECURE_HSTS_SECONDS = 3600  # MOD
