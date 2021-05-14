# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.conf import settings


def init_logging():
    if settings.DO_LOGGING:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                            format="%(asctime)s - %(levelname)s - %(message)s"
                            )


def debug(msg):
    logging.debug(msg)


logInitDone = False
if not logInitDone:
    logInitDone = True
    init_logging()
