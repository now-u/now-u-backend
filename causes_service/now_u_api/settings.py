"""
Django settings for now_u_api project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from dotenv import load_dotenv
from corsheaders.defaults import default_headers
from django.templatetags.static import static

from pathlib import Path
import sentry_sdk
import os

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise Exception(f"{name} is not set")
    return value

DEBUG = os.getenv('DEBUG', None) == 'true'

sentry_sdk.init(
    dsn="https://8e0da4fb2583f5ed5dbe5260f61362ab@o1209445.ingest.sentry.io/4506350920925184",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0 if DEBUG else 0.1,
)

BASE_URL = os.getenv('BASE_URL', 'http://192.168.1.11:8000')

print(f"{BASE_URL=}")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=2ni(vbte78nlvoip2+*pydk8(+z4ewov&8ns9+$6%5*b%dqhe'

X_FRAME_OPTIONS = 'SAMEORIGIN'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [BASE_URL]


# Application definition

INSTALLED_APPS = [
    'causes.apps.CausesConfig',
    'users.apps.UsersConfig',
    'images.apps.ImagesConfig',
    'faqs.apps.FaqConfig',
    'blogs.apps.BlogsConfig',

    # Admin
    'unfold',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_saml2_auth',

    # Health checks
    'health_check',
    'health_check.db',
    'health_check.storage',
    'health_check.contrib.migrations',
]

MIDDLEWARE = [
    'log_request_id.middleware.RequestIDMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "log_request_id.filters.RequestIDFilter"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filters": ["request_id"],
            "filename": "application.log",
            "formatter": "verbose",
            "maxBytes": 10485760, # 10 MB
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
        }
    },
    "formatters": {
        "verbose": {
            "format": "{asctime} {request_id} ({levelname})- {name}- {message}",
            "style": "{",
        }
    },
}

GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
REQUEST_ID_RESPONSE_HEADER = "REQUEST_ID"

ROOT_URLCONF = 'now_u_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'now_u_api.wsgi.application'

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http:\/\/localhost:*([0-9]+)?$",
    r"^https://\w+\.now-u\.com$",
]
CORS_ALLOW_HEADERS = (
    *default_headers,
    "Authorization",
)


STATIC_FILES_STORAGE_CONTAINER = os.getenv("STATIC_FILES_STORAGE_CONTAINER")
USING_AZURE_STORAGE = STATIC_FILES_STORAGE_CONTAINER is not None

if USING_AZURE_STORAGE:
    STATIC_FILES_STORAGE_ACCOUNT_NAME = get_required_env("STATIC_FILES_STORAGE_ACCOUNT_NAME")
    STATIC_FILES_STORAGE_ACCOUNT_KEY = get_required_env("STATIC_FILES_STORAGE_ACCOUNT_KEY")
    STATIC_FILES_STORAGE_DOMAIN = os.getenv("STATIC_FILES_STORAGE_DOMAIN")

    STORAGES = {
        # TODO Maybe use non public container for this, set AZURE_CONTAINER
        # TODO If not then remove custom backend and use the above vars 
        # https://django-storages.readthedocs.io/en/latest/backends/azure.html#install
        "default": {"BACKEND": "now_u_api.storage.PublicAzureStorage"},
        "staticfiles": {"BACKEND": "now_u_api.storage.PublicAzureStorage"},
    }

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_required_env('DATABASE_NAME'),
        'USER': get_required_env('DATABASE_USER'),
        'PASSWORD': get_required_env('DATABASE_PASSWORD'),
        'HOST': get_required_env('DATABASE_HOST'),
        'PORT': get_required_env('DATABASE_PORT'),
    }
}


AUTH_USER_MODEL = 'users.User'

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

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # TODO Add base authentication class which lets you authenticate if you are logged into admin
        'now_u_api.authentication.NowuTokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'now-u cause API',
    'DESCRIPTION': 'now-u service to fetch causes data',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
}

SAML2_AUTH_METADATA_FILE_PATH = os.getenv('SAML2_AUTH_METADATA_FILE_PATH', os.path.join(BASE_DIR, 'GoogleIDPMetadata.xml'))
assert os.path.isfile(SAML2_AUTH_METADATA_FILE_PATH)

SAML2_AUTH = {
    'DEBUG': True,
    'LOGGING': {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] %(message)s',
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                # 'stream': 'ext://sys.stdout',
                'level': 'DEBUG',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'saml2': {
                'level': 'DEBUG'
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': [
                'stdout',
            ],
        },
    },
    # Metadata is required, choose either remote url or local file path
    'METADATA_LOCAL_FILE_PATH': SAML2_AUTH_METADATA_FILE_PATH,

    # Optional settings below
    'DEFAULT_NEXT_URL': '/admin',  # Custom target redirect URL after the user get logged in. Default to /admin if not set. This setting will be overwritten if you have parameter ?next= specificed in the login URL.
    'CREATE_USER': 'TRUE', # Create a new Django user when a new user logs in. Defaults to True.
    'NEW_USER_PROFILE': {
        'USER_GROUPS': [],  # The default group name when a new user logs in
        'ACTIVE_STATUS': True,  # The default active status for new users
        'STAFF_STATUS': True,  # The staff status for new users
        'SUPERUSER_STATUS': False,  # The superuser status for new users
    },
    'ATTRIBUTES_MAP': {  # Change Email/UserName/FirstName/LastName to corresponding SAML2 userprofile attributes.
        'email': 'Email',
        'first_name': 'FirstName',
        'last_name': 'LastName',
        'groups': 'Groups',
    },
    # TODO Setup seeds for these groups with correct perms
    # NOTE: This must be in sync with https://admin.google.com/u/2/ac/apps/saml/610221347403/attrmapping
    'GROUPS_MAP': {
        'campaigns': 'Campaigns',
        'dev': 'Development',
        'Marketing & Comms': 'Marketing',
    },
    # 'AUTHN_REQUESTS_SIGNED': False,
    # 'WANT_ASSERTIONS_SIGNED': True,
    'WANT_RESPONSE_SIGNED': False,
    'TRIGGER': {
        # 'CREATE_USER': 'path.to.your.new.user.hook.method',
    #     # 'BEFORE_LOGIN': 'path.to.your.login.hook.method',
    },
    'ASSERTION_URL': BASE_URL, # Custom URL to validate incoming SAML requests against
    'ENTITY_ID': f'{BASE_URL}/saml2_auth/acs/', # Populates the Issuer element in authn request
    # 'NAME_ID_FORMAT': FormatString, # Sets the Format property of authn NameIDPolicy element
    'USE_JWT': False, # Set this to True if you are running a Single Page Application (SPA) with Django Rest Framework (DRF), and are using JWT authentication to authorize client users
    # 'FRONTEND_URL': 'https://myfrontendclient.com', # Redirect URL for the client if you are using JWT auth with DRF. See explanation below
    'TOKEN_REQUIRED': False,
}

# TODO Assert not none and secret if is
JWT_SECRET = get_required_env('JWT_SECRET')

MAILCHIMP = {
    'API_KEY': get_required_env('MAILCHIMP_API_KEY'),
    'LIST_ID': get_required_env('MAILCHIMP_LIST_ID'),
    'SERVER': get_required_env('MAILCHIMP_SERVER'),
}


class MEILISEARCH:
    URL = get_required_env('MEILISEARCH_URL')
    MASTER_KEY = get_required_env('MEILISEARCH_MASTER_KEY')

class SUPABASE:
    URL = get_required_env('SUPABASE_URL')
    KEY = get_required_env('SUPABASE_KEY')

UNFOLD = {
    "SITE_TITLE": "now-u admin",
    "SITE_HEADER": 'now-u admin',
    "SITE_LOGO": {
        "light": lambda _: static("now-u-logo-horizontal-orange.svg"),
        "dark": lambda _: static("now-u-logo-horizontal-orange.svg"),
    },
    "COLORS": {
        "primary": {
            "50": "#FFFAF5",
            "100": "#FFF8F0",
            "200": "#FFEEDB",
            "300": "#FFE7CC",
            "400": "#FFC88A",
            "500": "#FFA947",
            "600": "#FF8A05",
            "700": "#C76A00",
            "800": "#854700",
            "900": "#422300",
            "950": "#1F1000",
        },
    },
    "STYLES": [
        lambda request: static("css/ts-styles.css"),
    ],
    "DASHBOARD_CALLBACK": "admin.views.dashboard_callback",
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

class APP_LINKS_SERVICE:
    URL = get_required_env('APP_LINKS_SERVICE_URL')
    API_KEY = get_required_env('APP_LINKS_SERVICE_API_KEY')
