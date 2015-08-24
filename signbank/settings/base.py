from signbank.settings.settings_secret import *
# Django settings for signbank project.

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

EMAIL_HOST = ""

MANAGERS = ADMINS

TIME_ZONE = 'Europe/Helsinki'

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'fi'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = (
    '/home/heilniem/signbank-fi/locale',
)

LANGUAGES = (
    ('fi', 'Finnish'),
    ('en', 'English'),
)

MEDIA_ROOT = '/home/heilniem/signbank-fi/media'
MEDIA_URL = '/media/'

# Ditto for static files from the Auslan site (css, etc) with trailing slash
AUSLAN_STATIC_PREFIX = "/static/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "media"),
)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)
# The order of middleware classes is critical
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

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.template.context_processors.debug",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.i18n",
    "django.template.context_processors.tz",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "signbank.pages.context_processors.menu",
    "django.template.context_processors.csrf",
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

# add the Email backend to allow logins using email as username
AUTHENTICATION_BACKENDS = (
    "signbank.registration.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'signbank.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'signbank.wsgi.application'

# The order of apps matters!
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

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# TODO: Test the logging and improve it
# turn on lots of logging or not
DO_LOGGING = False
LOG_FILENAME = "debug.log"

# Application settings for signbank

# Settings controlling page contents

# what do we call this signbank?
LANGUAGE_NAME = "FinSL"
COUNTRY_NAME = "Finland"

# do we implement safe search for anonymous users?
# if True, any gloss that is tagged lexis:crude will be removed from
# search results for users who are not logged in
ANON_SAFE_SEARCH = False

# do we show the tag based search for anonymous users?
ANON_TAG_SEARCH = False

# TODO: I think this can be removed. This would allow the removal of gloss.sn too
# do we display the previous/next links to signs, requires gloss.sn to be
# used consistently
SIGN_NAVIGATION = False

# TODO: Do something with these, remove or see if they need correction?
# which definition fields do we show and in what order?
DEFINITION_FIELDS = ['general', 'noun', 'verb', 'interact',
                     'deictic', 'modifier', 'question', 'augment', 'note']

ADMIN_RESULT_FIELDS = ['idgloss', 'annotation_idgloss_jkl', 'annotation_idgloss_hki', 'annotation_comments']
# If you want to show English glosses, add these back to ADMIN_RESULT_FIELDS:
# 'annotation_idgloss_jkl_en', 'annotation_idgloss_hki_en'

# location and URL for uploaded files
UPLOAD_ROOT = MEDIA_ROOT + "upload/"
UPLOAD_URL = MEDIA_URL + "upload/"

# Location for comment videos relative to MEDIA_ROOT
COMMENT_VIDEO_LOCATION = "comments"
# Location for videos associated with pages
PAGES_VIDEO_LOCATION = 'pages'
# location for upload of videos relative to MEDIA_ROOT
# videos are stored here prior to copying over to the main
# storage location
VIDEO_UPLOAD_LOCATION = "upload"

# within MEDIA_ROOT we store newly uploaded videos in this directory
GLOSS_VIDEO_DIRECTORY = "video"

# which fields from the Gloss model should be included in the quick update
# form on the sign view
QUICK_UPDATE_GLOSS_FIELDS = ['language', 'dialect']

# should we always require a login for viewing dictionary content
ALWAYS_REQUIRE_LOGIN = True

# TODO: Remove this
# name of the primary css file, relative to the media directory
PRIMARY_CSS = "bootstrap_css/test-server.css"

# do we allow people to register for the site
ALLOW_REGISTRATION = True

ACCOUNT_ACTIVATION_DAYS = 7

# show the number signs page or an under construction page?
# TODO: remove this
SHOW_NUMBERSIGNS = True

LOGIN_REDIRECT_URL = '/'

# location of ffmpeg, used to convert uploaded videos
FFMPEG_PROGRAM = "/home/heilniem/ffmpeg-2.6.3-64bit-static/ffmpeg"
FFMPEG_TIMEOUT = 60
FFMPEG_OPTIONS = ["-vcodec", "h264", "-an"]

# defines the aspect ratio for videos
VIDEO_ASPECT_RATIO = 3.0 / 4.0

# settings for django-tagging
FORCE_LOWERCASE_TAGS = True

# TODO: Redo
# a list of tags we're allowed to use
ALLOWED_TAGS = ['',
                'workflow:needs video',
                'workflow:redo video',
                'workflow:problematic',
                ]
