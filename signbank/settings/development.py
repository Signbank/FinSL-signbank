from signbank.settings.base import *


TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'bootstrap_templates'),
)

# show emails on the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#PRIMARY_CSS = "bootstrap_css/bsl.css"
#PRIMARY_CSS = "bootstrap_css/auslan.css"
PRIMARY_CSS = "bootstrap_css/ngt.css"


# defines the aspect ratio for videos
#VIDEO_ASPECT_RATIO = 360.0/640.0


# TODO: Remove these lines, they are already in base.py
# what do we call this signbank?
LANGUAGE_NAME = "FinSL"
COUNTRY_NAME = "Finland"

# show/don't show sign navigation
SIGN_NAVIGATION = False

# show the number signs page or an under construction page?
#SHOW_NUMBERSIGNS = False

# do we show the 'advanced search' form and implement 'safe' search?
#ADVANCED_SEARCH = False

# which definition fields do we show and in what order?
#DEFINITION_FIELDS = []


#ADMIN_RESULT_FIELDS = ['idgloss', 'annotation_idgloss']

# Fixes the problem with merge TODO: Is this needed anymore?
# SOUTH_MIGRATION_MODULES = {
#    'tagging': 'tagging.south_migrations',
# }


GLOSS_VIDEO_DIRECTORY = 'glossvideo'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/heilniem/signbank-fi/debug.log',
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


import mimetypes
mimetypes.add_type("video/mp4", ".mov", True)


# a list of tags we're allowed to use
XALLOWED_TAGS = ['',
                 'workflow:needs video',
                 'workflow:redo video',
                 'workflow:problematic',
                 'corpus:attested',
                 'lexis:doubtlex',
                 'phonology:alternating',
                 'phonology:dominant hand only',
                 'phonology:double handed',
                 'phonology:forearm rotation',
                 'phonology:handshape change',
                 'phonology:onehand',
                 'phonology:parallel',
                 'phonology:symmetrical',
                 'phonology:two handed',
                 ]

DATABASE_NAME = '/home/heilniem/signbank-fi/signbank.db'
# TODO: Fix where this points at
WSGI_FILE = '/var/www2/signbank/live/virtualenv/signbank/lib/python2.7/site-packages/signbank/wsgi.py'
