# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from signbank.settings.base import *
# settings.base imports settings_secret
# The following settings are defined in settings_secret:
# SECRET_KEY, ADMINS, DATABASES, EMAIL_HOST, EMAIL_PORT, DEFAULT_FROM_EMAIL

# Debug should be True in development but not in production!
DEBUG = True

# A list of directories where Django looks for translation files.
LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

# The absolute path to the directory where collectstatic will collect static files for deployment.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
# This setting defines the additional locations the staticfiles app will traverse if the FileSystemFinder finder
# is enabled, e.g. if you use the collectstatic or findstatic management command or use the static file serving view.
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'signbank', 'static'),
)

# Set up a dummy cache for development, it doesn't actually cache anything.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = '/media/'

# location and URL for uploaded files
UPLOAD_ROOT = MEDIA_ROOT + 'upload/'
UPLOAD_URL = MEDIA_URL + 'upload/'

# To test emailing, use this to show emails in the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Turn on lots of logging
DO_LOGGING = True
LOG_FILENAME = 'debug.log'

if DEBUG:
    # Setting up debug toolbar.
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS += ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {'RESULTS_CACHE_SIZE': 100}
