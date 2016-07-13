"""Convert a video file to flv"""

from django.core.management.base import BaseCommand

from signbank.dictionary.models import Gloss


class Command(BaseCommand):

    help = 'generate a list of gloss IDs and their video URLs'
    args = ''

    def handle(self, *args, **options):

        for gloss in Gloss.objects.all():
            print gloss.id, gloss.get_video_url() # TODO: This will not work, get_video_url is removed from gloss
