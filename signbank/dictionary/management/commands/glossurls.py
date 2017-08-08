# -*- coding: utf-8 -*-
"""This command lists all Glosses and a list of each Glosses GlossVideos"""
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from signbank.dictionary.models import Gloss


class Command(BaseCommand):
    help = 'generate a list of gloss IDs and their video URLs'
    args = ''

    def handle(self, *args, **options):
        for gloss in Gloss.objects.all():
            print(gloss.id, gloss.glossvideo_set.all() or None)
