from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-v4(49a7)&zmj*sajpxm^m=v=!t5()uh8ec+4pti8x62_2g9=k+'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'AppHome',
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

ROOT_URLCONF = 'projetoDjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # --- CORREÇÃO PRINCIPAL ---
        # Agora o Django vai procurar por uma pasta 'templates' na raiz do seu projeto.
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'projetoDjango.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'pt-br'  # Corrigido para português
TIME_ZONE = 'America/Sao_Paulo' # Corrigido para fuso horário do Brasil
USE_I18N = True
USE_TZ = True


# --- CONFIGURAÇÃO DE ESTÁTICOS CORRIGIDA E SIMPLIFICADA ---
STATIC_URL = '/static/'

# O único lugar que o Django precisa procurar por seus arquivos estáticos.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# NÃO use WhiteNoise ou STATICFILES_STORAGE em modo de desenvolvimento (DEBUG=True).
# O servidor de desenvolvimento do Django já faz isso perfeitamente.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'