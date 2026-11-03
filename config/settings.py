import os
import django
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── oracledb como reemplazo de cx_Oracle para el backend Oracle de Django ─────
import sys
try:
    import oracledb

    # Parche de compatibilidad: en oracledb >= 2.0, Binary no es un tipo Python
    # real (clase), lo que rompe el isinstance() interno del backend Oracle de
    # Django. Lo sobreescribimos con `bytes`, que es el equivalente correcto.
    if not isinstance(oracledb.Binary, type):
        oracledb.Binary = bytes

    oracledb.version = "8.3.0"          # hace que Django lo trate como cx_Oracle 8
    sys.modules["cx_Oracle"] = oracledb  # alias SIEMPRE antes de init_oracle_client

    # Modo THICK requerido por Native Network Encryption del servidor Oracle.
    try:
        # Primero intenta con lib_dir explícito según el sistema operativo
        if sys.platform.startswith('win'):
            # Configuración anterior para Windows
            lib_dir_path = r"C:\oracle\instantclient_23_0"
        else:
            # Configuración para Linux (servidor)
            lib_dir_path = r"/usr/lib/oracle/19.29/client64/lib"
            
        oracle_client_dir = os.environ.get('ORACLE_CLIENT_DIR', lib_dir_path)
        
        if os.path.exists(oracle_client_dir):
            oracledb.init_oracle_client(lib_dir=oracle_client_dir)
        else:
            # Fallback: usa LD_LIBRARY_PATH / PATH del sistema
            oracledb.init_oracle_client()
    except Exception as _e:
        import warnings
        warnings.warn(
            f"[oracledb] No se pudo activar modo THICK. Error: {_e}",
            RuntimeWarning,
            stacklevel=2,
        )
except ImportError:
    pass
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-cambia-esto-en-produccion')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Aplicaciones locales
    'apps.empresas',
    'apps.pacientes',
    'apps.informes',
    'apps.turnos',
    'apps.preocupacional',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← debe ir justo después de Security
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

WSGI_APPLICATION = 'config.wsgi.application'

# ─── BASE DE DATOS ────────────────────────────────────────────────────────────
# SQLite  → tablas internas de Django (auth, sessions, migrations, admin)
# Oracle  → datos de negocio (pacientes, empresas, informes)

_ORACLE_DSN = (
    '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
    '(HOST=visionsalud.net.ar)(PORT=1521))'
    '(CONNECT_DATA=(SERVICE_NAME=dbospis_pdb1.sub04021222360.vcnospis10.oraclevcn.com)))'
)

DATABASES = {
    # Base de datos única: Oracle OCI
    # Auth, sessions, admin y datos de negocio en una sola plataforma
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': _ORACLE_DSN,
        'USER': 'visionsalud',
        'PASSWORD': os.getenv('ORACLE_PASSWORD'),
    },
}
# ─────────────────────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise: sirve archivos estáticos en producción con compresión GZip y cache
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# En entorno local (DEBUG=True), podemos hacer que apunte a OCI para ver archivos viejos.
# En producción (DEBUG=False), usamos la ruta relativa habitual.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ── CSRF / Sesión ────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 'http://127.0.0.1:8000',
    'http://localhost:8002', 'http://127.0.0.1:8002',
    'http://ospis:8002',
    'http://visionsalud.net.ar', 'http://visionsalud.net.ar:8002',
    'https://visionsalud.net.ar', 'https://visionsalud.net.ar:8002',
]
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

