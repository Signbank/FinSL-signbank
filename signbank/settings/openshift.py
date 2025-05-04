"""OpenShift production environment specific settings for FinSL-signbank."""
import os

from django.utils.translation import gettext_lazy as _

#: IMPORTANT: Debug should always be False in production
DEBUG = False

# The following settings are defined in environment variables:
# SECRET_KEY, ADMINS, DATABASES, EMAIL_HOST, EMAIL_PORT, DEFAULT_FROM_EMAIL
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-secret-key')
#: IMPORTANT: The hostname that this signbank runs on, this prevents HTTP Host header attacks
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
ADMINS = os.environ.get('DJANGO_ADMINS')

# Absolute path to the base directory of the application.
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# Path to the project directory.
PROJECT_DIR = os.path.dirname(BASE_DIR)
# Sets the field to automatically use for model primary key
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

CSRF_COOKIE_SECURE = os.environ.get('DJANGO_CSRF_COOKIE_SECURE', 'True').lower() in ('true',)
CSRF_TRUSTED_ORIGINS = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')

# A list in the same format as ADMINS that specifies who should get broken link notifications
# when BrokenLinkEmailsMiddleware is enabled. ADMINS are set in secret_settings.
try:
    MANAGERS = ADMINS
except NameError:
    MANAGERS = (("", ""),)

#: A string representing the time zone for this installation.
TIME_ZONE = 'Europe/Helsinki'

#: A string representing the language code for this installation. This should be in standard language ID format.
#: For example, U.S. English is "en-us".
LANGUAGE_CODE = 'fi'

# The ID, as an integer, of the current site in the django_site database table.
SITE_ID = 1
#: A boolean that specifies whether Django's translation system should be enabled.
USE_I18N = True
#: A boolean that specifies if localized formatting of data will be enabled by default or not.
USE_L10N = True
#: A boolean that specifies if datetimes will be timezone-aware by default or not.
USE_TZ = True
#: A list of all available languages.
#: The list is a list of two-tuples in the format (language code, language name) - for example, ('ja', 'Japanese').
LANGUAGES = (
    ('fi', _('Finnish')),
    ('sv', _('Swedish')),
    ('en', _('English')),
)

# URL to use when referring to static files located in STATIC_ROOT.
# Example: "/static/" or "http://static.example.com/"
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
#: The list of finder backends that know how to find static files in various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

#: A list of middleware classes to use. The order of middleware classes is critical!
MIDDLEWARE = [
    # If want to use some of the HTTPS settings in secret_settings, enable SecurityMiddleware
    #'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.csrf',
            ],
        },
    },
]

#: A list of authentication backend classes (as strings) to use when attempting to authenticate a user.
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
)

# A list of IP addresses, as strings: Allow the debug() context processor to add some variables to the template context.
INTERNAL_IPS = ('127.0.0.1',)

# A string representing the full Python import path to your root URLconf. For example: "mydjangoapps.urls".
ROOT_URLCONF = 'signbank.urls'


#: A list of strings designating all applications that are enabled in this Django installation.
#: Dotted Python path to: an application configuration class (preferred), or a package containing an application.
#: The order of the apps matter!
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'bootstrap3',
    'django_summernote',
    'signbank.dictionary',
    'django.contrib.flatpages',
    'signbank.contentpages',
    'signbank.video',
    'reversion',
    'tagging',
    'django_comments',
    'guardian',
    'notifications',
    'django.contrib.sitemaps',
)

# TODO: Evaluate how to handle flatpages migrations
MIGRATION_MODULES = {
    'flatpages': 'custom_migrations.flatpages',
}

ABSOLUTE_URL_OVERRIDES = {
    #: Allow using admin change url for notifications.
    'auth.user': lambda user: "/admin/auth/user/%s/change/" % user.id,
}

#: Location for upload of videos relative to MEDIA_ROOT, videos are stored here prior to copying over to the main
#: storage location
VIDEO_UPLOAD_LOCATION = "upload"

#: How many days a user has until activation time expires. Django-registration related setting.
ACCOUNT_ACTIVATION_DAYS = 7
#: A boolean indicating whether registration of new accounts is currently permitted.
REGISTRATION_OPEN = True

#: The URL where requests are redirected after login when the contrib.auth.login view gets no next parameter.
LOGIN_REDIRECT_URL = '/'

# For django-tagging: force tags to be lowercase.
FORCE_LOWERCASE_TAGS = True

import mimetypes
mimetypes.add_type("video/mp4", ".mov", True)
mimetypes.add_type("video/webm", ".webm", True)

# A list of directories where Django looks for translation files.
LOCALE_PATHS = (
    './locale',
)

AWS_S3_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID", "")
AWS_S3_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY", "")
AWS_S3_ENDPOINT_URL = os.environ.get("BUCKET_ENDPOINT_URL", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get("BUCKET_NAME", "")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.environ.get("AWS_S3_ACCESS_KEY_ID", ""),
            "secret_key": os.environ.get("AWS_S3_SECRET_ACCESS_KEY", ""),
            "bucket_name": os.environ.get("BUCKET_NAME", ""),
            "endpoint_url": os.environ.get("BUCKET_ENDPOINT_URL", ""),
            "region_name": os.environ.get("BUCKET_REGION_NAME", ""),
            "default_acl": "public-read",
            "querystring_auth": False,
            "location": "media",
        },
    },
    "staticfiles": {
        "BACKEND": "signbank.utils.StaticFilesStorage",
        "OPTIONS": {
            "access_key": os.environ.get("AWS_S3_ACCESS_KEY_ID", ""),
            "secret_key": os.environ.get("AWS_S3_SECRET_ACCESS_KEY", ""),
            "bucket_name": os.environ.get("BUCKET_NAME", ""),
            "endpoint_url": os.environ.get("BUCKET_ENDPOINT_URL", ""),
            "region_name": os.environ.get("BUCKET_REGION_NAME", ""),
            "default_acl": "public-read",
            "querystring_auth": False,
            "location": "static",
        },
    }
}

#: The absolute path to the directory where collectstatic will collect static files for deployment.
#: Example: "/var/www/example.com/static/"
STATIC_ROOT = '/static/'
# This setting defines the additional locations the staticfiles app will traverse if the FileSystemFinder finder
# is enabled, e.g. if you use the collectstatic or findstatic management command or use the static file serving view.
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "signbank", "static"),
)

#: Use Local-memory caching for specific views (if you have bigger needs, use something else).
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'finsl-signbank-localmemcache',
    }
}

#: Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '/media/'
# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

#: Location and URL for uploaded files.
UPLOAD_ROOT = MEDIA_ROOT + "upload/"
UPLOAD_URL = MEDIA_URL + "upload/"

#: The backend to use for sending emails.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

#: A sample logging configuration. The only tangible logging
#: performed by this configuration is to send an email to
#: the site admins on every HTTP 500 error when DEBUG=False.
#: See http://docs.djangoproject.com/en/stable/topics/logging for
#: more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#: Turn off lots of logging.
DO_LOGGING = False
LOG_FILENAME = "debug.log"
