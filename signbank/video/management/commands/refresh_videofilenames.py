# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys
from django.core.management.base import BaseCommand
from signbank.video.models import GlossVideo
from signbank.dictionary.models import Gloss


def eprint(*args, **kwargs):
    """Printing errors in a way that supports python3 too"""
    print(*args, file=sys.stderr, **kwargs)


class Command(BaseCommand):
    help = 'Moves GlossVideos to correct folders and renames the filenames to the correct format.'
    args = ''

    def handle(self, *args, **options):
        firsterror = True
        for gloss in Gloss.objects.all():
            # Rename all the videos of a gloss to the correct form
            """
            Using this function instead of GlossVideo.objects.all() because it holds the filenaming convention.
            Also this hopefully makes sure that we don't rename GlossVideos based on possibly outdated foreignkey data,
            because we want to name GlossVideos according to Gloss coupled with GlossVideo.pk.
            """
            try:
                GlossVideo.rename_glosses_videos(gloss)
            except OSError as err:
                if firsterror:
                    firsterror = False
                    eprint("OSError, the following files did not exist:\n-------------------------------------------")
                eprint(err)
