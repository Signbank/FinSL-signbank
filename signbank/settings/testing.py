# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from signbank.settings.development import *

# Always use local file storage when running tests
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
GLOSS_VIDEO_FILE_STORAGE = 'signbank.video.models.GlossVideoStorage'
