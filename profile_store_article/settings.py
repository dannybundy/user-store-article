from pathlib import Path
import cloudinary, dotenv, os, sys


BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


dotenv_file = os.path.join(BASE_DIR, "panaleener.env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

SECRET_KEY = os.environ['SECRET_KEY']


DEBUG = True


ALLOWED_HOSTS = [
    'localhost',
    '0.0.0.0',
    '127.0.0.1',
    'user-template.herokuapp.com'
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'article',
    'store',
    'user_profile',
    'bootstrap_modal_forms',
    'ckeditor',
    'cloudinary',
    'csp',
    'crispy_forms',
    'django_countries',
    'django_extensions',
    'django_tables2',
    'phonenumber_field',
    'rangefilter',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'profile_store_article.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], #os.path.join(BASE_DIR, 'apps/user_profile', 'templates'),
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


WSGI_APPLICATION = 'profile_store_article.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ['POSTGRES_NAME'],
#         'HOST': os.environ['POSTGRES_HOST'],
#         'PORT': os.environ['POSTGRES_PORT'],
#         'USER': os.environ['POSTGRES_USER'],
#         'PASSWORD': os.environ['POSTGRES_PASSWORD'],
#     }
# }

if 'test' in sys.argv or 'test_coverage' in sys.argv: #Covers regular testing and django-coverage
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'


# Cloudinary database
cloudinary.config(
  cloud_name = os.environ['CLOUD_NAME'],
  api_key = os.environ['API_KEY'],
  api_secret = os.environ['API_SECRET'],
  secure = True
)


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Authentication
LOGIN_URL = 'profile:login'


# Static/Media files
STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR).joinpath('staticfiles')
STATICFILES_DIRS = [Path(BASE_DIR).joinpath('static')]
STATIC_TMP = os.path.join(BASE_DIR, 'static')
os.makedirs(STATIC_TMP, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)

MEDIA_URL='/media/'
MEDIA_ROOT=Path(BASE_DIR).joinpath('media')


# Crispy forms
CRISPY_TEMPLATE_PACK = "bootstrap4"


# Twilio
ACCOUNT_SID = os.environ['ACCOUNT_SID']
AUTH_TOKEN = os.environ['AUTH_TOKEN']
TRIAL_NUMBER = os.environ['TRIAL_NUMBER']


# Stripe
STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']
STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
STRIPE_ENDPOINT_SECRET = os.environ['STRIPE_ENDPOINT_SECRET']


# Email
EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = os.environ['EMAIL_HOST_USER']


# Ckeditor
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'