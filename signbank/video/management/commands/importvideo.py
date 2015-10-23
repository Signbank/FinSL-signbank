"""Convert a video file to flv"""

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from signbank.video.models import GlossVideo
from models import Gloss
import os


class Command(BaseCommand):

    help = 'import existing videos into the database'
    args = 'path'

    def handle(self, *args, **options):

        if len(args) == 1:
            path = args[0]

            import_existing_gloss_videos(path)

        else:
            print "Usage importvideo", self.args


def import_existing_gloss_videos(path):
    from django.db import connection, transaction
    from django.db.models import Max

    cursor = connection.cursor()

    # delete all existing videos
    GlossVideo.objects.all().delete()

    # find the largest currently used id
    id = GlossVideo.objects.all().aggregate(Max('id'))['id__max']
    if id is None:
        id = 0

    basedir = settings.MEDIA_ROOT

    # scan the directory and make an entry for each video file found
    for dir in os.listdir(os.path.join(basedir, path)):
        if os.path.isdir(os.path.join(basedir, path, dir)):
            for videofile in os.listdir(os.path.join(basedir, path, dir)):
                ext = os.path.splitext(videofile)
                if ext in ['.mp4']:
                    id += 1
                    fullpath = os.path.join(path, dir, videofile)
                else:
                    print 'skipping ', videofile

    transaction.commit_unless_managed()
