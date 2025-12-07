"""
Django settings for pit_sistema project.
"""

from pathlib import Path
import os

# ---------------------------
# Paths
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------
# Seguridad y debug
# ---------------------------
SECRET_KEY = 'django-insecure-9@yzuvt=ne8&c68ltt)z=m1!uw&k7eenv_1y*x9&onp7aj01$5'
DEBUG = True
ALLOWED_HOSTS = ['*']

# ---------------------------
# Aplicaciones
# ---------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus apps
    'apps.users.apps.UsersConfig',
    'apps.academic.apps.AcademicConfig',
    'apps.tutoring.apps.TutoringConfig',
    'apps.jefe_depto.apps.JefeDeptoConfig',
    'apps.coordinst.apps.CoordinstConfig',
    'apps.coordac.apps.CoordacConfig',
    'apps.tutee.apps.TuteeConfig',
    'apps.jefe_deptodes.apps.JefeDeptodesConfig',
    'apps.psychologist.apps.PsychologistConfig',
]

# ---------------------------
# Middleware
# ---------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pit_sistema.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # 👈 AQUÍ EL CAMBIO
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


WSGI_APPLICATION = 'pit_sistema.wsgi.application'

# ---------------------------
# Base de datos mínima (solo para Django internamente)
# ---------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tutorias',     # p.ej. 'mi_proyecto'
        'USER': 'root',    # p.ej. 'root'
        'PASSWORD': '',     # p.ej. '123456'
        'HOST': 'localhost',           # o IP/host del servidor
        'PORT': '3306',                # puerto por defecto de MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# ---------------------------
# Sesiones en cookies (no depende de DB ni Redis)
# ---------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_SAVE_EVERY_REQUEST = True

# ---------------------------
# Password validation
# ---------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ---------------------------
# Internacionalización
# ---------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# ---------------------------
# Archivos media y estáticos
# ---------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# ---------------------------
# Configuración de auth
# ---------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/tutoring/'
LOGOUT_REDIRECT_URL = '/'
