""" Models for the video application
keep track of uploaded videos and converted versions
"""

from django.db import models
from django.conf import settings
from django.dispatch import receiver
import os
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from convertvideo import extract_frame, convert_video


class VideoPosterMixin(object):
    """Base class for video models that adds a method
    for generating poster images

    Concrete class should have fields 'videofile' and 'poster'
    """

    def process(self):
        """The clean method will try to validate the video
        file format, optimise for streaming and generate
        the poster image"""

        self.poster_path()
        # self.ensure_mp4()

    def poster_path(self, create=True):
        """Return the path of the poster image for this
        video, if create=True, create the image if needed
        Return None if create=False and the file doesn't exist"""

        vidpath, ext = os.path.splitext(self.videofile.path)
        poster_path = vidpath + ".jpg"

        if not os.path.exists(poster_path):
            if create:
                # need to create the image
                extract_frame(self.videofile.path, poster_path)
            else:
                return None

        return poster_path

    def poster_url(self):
        """Return the URL of the poster image for this video"""

        # generate the poster image if needed
        path = self.poster_path()

        # splitext works on urls too!
        vidurl, ext = os.path.splitext(self.videofile.url)
        poster_url = vidurl + ".jpg"

        return poster_url

    def get_absolute_url(self):

        return self.videofile.url

    def ensure_mp4(self):
        """Ensure that the video file is an h264 format
        video, convert it if necessary"""

        # convert video to use the right size and iphone/net friendly bitrate
        # create a temporary copy in the new format
        # then move it into place

        # print "ENSURE: ", self.videofile.path

        (basename, ext) = os.path.splitext(self.videofile.path)
        tmploc = basename + "-conv.mp4"
        err = convert_video(self.videofile.path, tmploc, force=True)
        # print tmploc
        shutil.move(tmploc, self.videofile.path)

    def delete_files(self):
        """Delete the files associated with this object"""

        try:
            os.unlink(self.videofile.path)
            poster_path = self.poster_path(create=False)
            if poster_path:
                os.unlink(poster_path)
        except IOError:
            pass


class Video(models.Model, VideoPosterMixin):
    """A video file stored on the site"""

    # video file name relative to MEDIA_ROOT
    videofile = models.FileField(
        # Translators: Video: videofile
        _("Video file in h264 mp4 format"), upload_to=settings.VIDEO_UPLOAD_LOCATION)

    def __unicode__(self):
        return self.videofile.name


import shutil


class GlossVideoStorage(FileSystemStorage):
    """Implement our shadowing video storage system"""

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.STATIC_URL):  # TODO: base_url: media or static?
        super(GlossVideoStorage, self).__init__(location, base_url)

    def get_valid_name(self, name):
        """Generate a valid name, we use directories named for the
        first two digits in the filename to partition the videos"""

        (targetdir, basename) = os.path.split(name)

        path = os.path.join(unicode(basename)[:2], unicode(basename))

        result = os.path.join(targetdir, path)

        return result


storage = GlossVideoStorage()


class GlossVideo(models.Model, VideoPosterMixin):
    """A video that represents a particular idgloss"""

    videofile = models.FileField(
        "video file", upload_to=settings.GLOSS_VIDEO_DIRECTORY, storage=storage)
    gloss = models.ForeignKey('dictionary.Gloss')

    # video version, version = 0 is always the one that will be displayed
    # we will increment the version (via reversion) if a new video is added
    # for this gloss
    # Translators: GlossVideo: version
    version = models.IntegerField(_("Version"), default=0)

    # TODO: Keep this or not?
    def reversion(self, revert=False):
        """We have a new version of this video so increase
        the version count
        unless revert=True, in which case we go the other
        way and decrease the version number"""

        if revert:
            self.version -= 1
        else:
            self.version += 1

        # Remove the post image if present, it will be regenerated
        poster = self.poster_path(create=False)
        if poster is not None:
            os.unlink(poster)
        self.save()

    @staticmethod
    def create_filename(idgloss, glosspk, videopk):
        """Returns a correctly named filename"""
        return idgloss + "-" + str(glosspk) + "_vid" + str(videopk) + ".mp4"

    @staticmethod
    def gloss_has_videos(gloss):
        """Returns True if the specified Gloss has any videos"""
        return True if GlossVideo.objects.filter(gloss=gloss).exists() else False

    @staticmethod
    def get_glosses_videos(gloss):
        """Returns all glossvideos for selected Gloss"""
        return GlossVideo.objects.filter(gloss=gloss)

    @staticmethod
    def rename_glosses_videos(gloss):
        """Renames the filenames of selected Glosses videos to match the Gloss name"""
        glossvideos = GlossVideo.objects.filter(gloss=gloss)
        for glossvideo in glossvideos:
            # Create the base filename for the video based on the new gloss.idgloss
            new_filename = GlossVideo.create_filename(gloss.idgloss, gloss.pk, glossvideo.pk)

            # Create new_path by joining 'glossvideo' and the two first letters from gloss.idgloss
            new_path = os.path.join('glossvideo', unicode(gloss.idgloss[:2]), new_filename)

            try:
                # Rename the file in the system, get old_path from glossvideo.videofile.path, join new_path with MEDIA_ROOT
                os.renames(glossvideo.videofile.path, os.path.join(settings.MEDIA_ROOT, new_path))
            except IOError:
                # If there is a problem moving the file, don't change glossvideo.videofile, it would not match
                continue

            # Change the glossvideo.videofile to the new path
            glossvideo.videofile = new_path
            glossvideo.save()

    def __unicode__(self):
        return self.videofile.name


@receiver(models.signals.pre_delete, sender=GlossVideo)
def delete_on_delete(sender, instance, **kwargs):
    """On signal delete, use pre_delete to delete the videofile. This will happen when a GlossVideo object is deleted"""
    if instance.videofile:
        if os.path.isfile(instance.videofile.path):
            os.remove(instance.videofile.path)
