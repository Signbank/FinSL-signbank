"""This command lists all Glosses and a list of each Glosses GlossVideos"""
from django.core.management.base import BaseCommand
from signbank.dictionary.models import Gloss
from signbank.video.models import GlossVideo


class Command(BaseCommand):
    help = 'generate a list of gloss IDs and their video URLs'
    args = ''

    def handle(self, *args, **options):
        for gloss in Gloss.objects.all():
            print gloss.id, GlossVideo.get_glosses_videos(gloss)
