from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = 'ytj5ars5xlyaw9sd6t8uoc-^f5=)6p4!j_j2jnffc08xf@+3zd'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'gieapp.onrender.com']
CSRF_TRUSTED_ORIGINS = ['https://gieapp.onrender.com']


# Aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fichador',
    'usuarios',
    'tareas',
    'reservas',
    'ventas',
    'clientes',
    'widget_tweaks',
    'stock',
    'crispy_forms',
    'crispy_bootstrap5',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Middlewares
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gie_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gie_project.wsgi.application'

# Base de datos (PostgreSQL en Render)
DATABASES = {
    'default': dj_database_url.parse(
        'postgresql://gie_db_user:aVhdKpVGwwUCJIZV8C9kRed2tekPT1ag@dpg-d13dmfjipnbc73b70shg-a/gie_db',
        conn_max_age=600
    )
}

# Validaciones de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True
USE_L10N = True

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'gie_project' / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración personalizada
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'usuarios.CustomUser'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'panel_principal'
LOGOUT_REDIRECT_URL = '/'

# Correo (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'gieintelligence@gmail.com'
EMAIL_HOST_PASSWORD = 'olxq zeok imef ofve'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
