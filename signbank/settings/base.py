from signbank.settings.settings_secret import *
from django.utils.translation import ugettext_lazy as _
import os
# Django settings for Signbank project.
# *** In development run bin/development.py to use development settings.
# *** In production run bin/production.py to use production settings.
# settings_secret.py is imported in this settings file, you should put the sensitive information in that file.

# Absolute path to the base directory of the application.
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# Path to the project directory.
PROJECT_DIR = os.path.dirname(BASE_DIR)

# A list in the same format as ADMINS that specifies who should get broken link notifications
# when BrokenLinkEmailsMiddleware is enabled. ADMINS are set in secret_settings.
MANAGERS = ADMINS

# A string representing the time zone for this installation.
TIME_ZONE = 'Europe/Helsinki'

# A string representing the language code for this installation. This should be in standard language ID format.
# For example, U.S. English is "en-us".
LANGUAGE_CODE = 'fi'

# The ID, as an integer, of the current site in the django_site database table.
SITE_ID = 1
# A boolean that specifies whether Django's translation system should be enabled.
USE_I18N = True
# A boolean that specifies if localized formatting of data will be enabled by default or not.
USE_L10N = True
# A boolean that specifies if datetimes will be timezone-aware by default or not.
USE_TZ = True
# A list of all available languages.
# The list is a list of two-tuples in the format (language code, language name) - for example, ('ja', 'Japanese').
LANGUAGES = (
    ('fi', _('Finnish')),
    ('en', _('English')),
)

# URL to use when referring to static files located in STATIC_ROOT.
# Example: "/static/" or "http://static.example.com/"
STATIC_URL = '/static/'
# The list of finder backends that know how to find static files in various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Used by stylesheet.py to allow usage of the template tag {% primary_css %]
PRIMARY_CSS = "bootstrap_css/signbank.css"

# A list of middleware classes to use. The order of middleware classes is critical!
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'signbank.pages.middleware.PageFallbackMiddleware',
    #    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

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
                'signbank.pages.context_processors.menu',
            ],
        },
    },
]

# A list of authentication backend classes (as strings) to use when attempting to authenticate a user.
AUTHENTICATION_BACKENDS = (
    "signbank.registration.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)

# A list of IP addresses, as strings: Allow the debug() context processor to add some variables to the template context.
INTERNAL_IPS = ('127.0.0.1',)

# A string representing the full Python import path to your root URLconf. For example: "mydjangoapps.urls".
ROOT_URLCONF = 'signbank.urls'

# The full Python path of the WSGI application object that Django's built-in servers (e.g. runserver) will use.
WSGI_APPLICATION = 'signbank.wsgi.application'

# A list of strings designating all applications that are enabled in this Django installation.
# Dotted Python path to: an application configuration class (preferred), or a package containing an application.
# The order of the apps matter!
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
    'signbank.feedback',
    'signbank.registration',
    'signbank.pages',
    'signbank.video',
    'reversion',
    'tagging',
)

# If True, any gloss that is tagged lexis:crude will be removed from search results for users who are not logged in.
ANON_SAFE_SEARCH = False

# Set the fields to show in search results (translation equivalents are defined in the template)
ADMIN_RESULT_FIELDS = ['dataset', 'idgloss', 'idgloss_en', 'annotation_comments']

# Location for comment videos relative to MEDIA_ROOT, comment videos are feedback videos.
COMMENT_VIDEO_LOCATION = "comments"
# Location for videos associated with pages, pages videos are uploaded for a static page.
PAGES_VIDEO_LOCATION = "pages"
# Location for upload of videos relative to MEDIA_ROOT, videos are stored here prior to copying over to the main
# storage location
VIDEO_UPLOAD_LOCATION = "upload"

# Allow people to register to the site. This is related to django-registration (which is included in source atm).
ALLOW_REGISTRATION = True
# How many days a user has until activation time expires. Django-registration related setting.
ACCOUNT_ACTIVATION_DAYS = 7

# The URL where requests are redirected after login when the contrib.auth.login view gets no next parameter.
LOGIN_REDIRECT_URL = '/'

# location of ffmpeg, used to convert uploaded videos
FFMPEG_PROGRAM = "../ffmpeg"
FFMPEG_TIMEOUT = 60
FFMPEG_OPTIONS = ["-vcodec", "h264", "-an"]

# Defines the aspect ratio for videos
VIDEO_ASPECT_RATIO = 3.0 / 4.0

# For django-tagging: force tags to be lowercase.
FORCE_LOWERCASE_TAGS = True

import mimetypes
mimetypes.add_type("video/mp4", ".mov", True)