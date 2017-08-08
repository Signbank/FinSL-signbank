""" Models for the video application keep track of uploaded videos and converted versions"""
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
from django.dispatch import receiver
import os
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage


@python_2_unicode_compatible
class Video(models.Model):
    """A video file stored on the site"""

    # video file name relative to MEDIA_ROOT
    videofile = models.FileField(
        # Translators: Video: videofile
        _("Video file in h264 mp4 format"), upload_to=settings.VIDEO_UPLOAD_LOCATION)

    def __str__(self):
        return self.videofile.name


class GlossVideoStorage(FileSystemStorage):
    """Implement our shadowing video storage system"""

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        super(GlossVideoStorage, self).__init__(location, base_url)

    def get_valid_name(self, name):
        """Generate a valid name, we use directories named for the
        first two digits in the filename to partition the videos"""

        (targetdir, basename) = os.path.split(name)
        path = os.path.join(str(basename)[:2].upper(), str(basename))
        result = os.path.join(targetdir, path)

        return result

    def url(self, name):
        return settings.MEDIA_URL + name


storage = GlossVideoStorage()


@python_2_unicode_compatible
class GlossVideo(models.Model):
    """A video that represents a particular idgloss"""

    title = models.CharField(_("Title"), blank=True, unique=False, max_length=100,
                             help_text=_("Descriptive name of the video."))
    videofile = models.FileField(_("Video file"), upload_to=settings.GLOSS_VIDEO_DIRECTORY, storage=storage,
                                 help_text=_("Video file."))
    posterfile = models.FileField(_("Poster file"), upload_to=os.path.join(settings.GLOSS_VIDEO_DIRECTORY, "posters"),
                                  storage=storage, blank=True, help_text=_("Still image representation of the video."),
                                  default="")
    gloss = models.ForeignKey('dictionary.Gloss', verbose_name=_("Gloss"), null=True,
                              help_text=_("The gloss this GlossVideo is related to."))
    dataset = models.ForeignKey('dictionary.Dataset', verbose_name=_("Glossvideo dataset"), null=True,
                                help_text=_("Dataset of a GlossVideo, derived from gloss (if any) or chosen when video "
                                            "was uploaded."))
    # Translators: GlossVideo: version
    version = models.IntegerField(_("Version"), default=0,
                                  help_text=_("A number that represents the order of the Glossvideo's in "
                                              "a gloss page. Smaller number means higher priority."))

    class Meta:
        ordering = ['version']

    def save(self, *args, **kwargs):
        # Save object so that we can access the saved fields.
        super(GlossVideo, self).save(*args, **kwargs)
        # If the GlossVideo object has a Gloss set, rename that glosses videos (that aren't correctly named).
        if self.videofile and hasattr(self, 'gloss') and self.gloss is not None:
            self.rename_video()
        try:
            self.dataset = self.gloss.dataset
        except AttributeError:
            pass

    def get_absolute_url(self):
        return self.videofile.url

    def rename_video(self):
        """Rename the video and the video to correct path if the glossvideo object has a foreignkey to a gloss."""
        # Do not rename the file if glossvideo doesn't have a gloss.
        if hasattr(self, 'gloss') and self.gloss is not None:
            # Get file extensions
            ext = os.path.splitext(self.videofile.path)[1]
            # Create the base filename for the video based on the new self.gloss.idgloss
            new_filename = GlossVideo.create_filename(self.gloss.idgloss, self.gloss.pk, self.pk, ext)
            # Create new_path by joining 'glossvideo' and the two first letters from gloss.idgloss
            new_path = os.path.join('glossvideo', str(self.gloss.idgloss[:2]).upper(), new_filename)
            full_new_path = os.path.join(settings.MEDIA_ROOT, new_path)

            # Check if a file already exists in the path we try to save to or if this file already is in that path.
            if not (os.path.isfile(full_new_path) or self.videofile == new_path):
                try:
                    # Rename the file in the system, get old_path from self.videofile.path.
                    os.renames(self.videofile.path, full_new_path)
                except IOError:
                    # If there is a problem moving the file, don't change self.videofile, it would not match
                    return
                except OSError:
                    # If the sourcefile does not exist, raise OSError
                    raise OSError(str(self.pk) + ' ' + str(self.videofile))

                # Change the self.videofile to the new path
                self.videofile = new_path
                self.save()

    @staticmethod
    def create_filename(idgloss, glosspk, videopk, ext):
        """Returns a correctly named filename"""
        return str(idgloss) + "-" + str(glosspk) + "_vid" + str(videopk) + ext

    def create_poster_filename(self, ext):
        """Returns a preferred filename of posterfile. Ext is the file extension without the dot."""
        if self.gloss:
            return str(self.gloss.idgloss) + "-" + str(self.gloss.pk) + "_vid" + str(self.pk) + "_poster." + ext
        return self.videofile.name + "." + ext

    @staticmethod
    def rename_glosses_videos(gloss):
        """Renames the filenames of selected Glosses videos to match the Gloss name"""
        glossvideos = GlossVideo.objects.filter(gloss=gloss)
        for glossvideo in glossvideos:
            glossvideo.rename_video()

    def get_extension(self):
        """Returns videofiles extension."""
        return os.path.splitext(self.videofile.path)[1]

    def has_poster(self):
        """Returns true if the glossvideo has a poster file."""
        if self.posterfile:
            return True
        return False

    def __str__(self):
        return self.videofile.name


@receiver(models.signals.pre_delete, sender=GlossVideo)
def delete_on_delete(sender, instance, **kwargs):
    """On signal delete, use pre_delete to delete the videofile. This will happen when a GlossVideo object is deleted"""
    if instance.videofile:
        if os.path.isfile(instance.videofile.path):
            os.remove(instance.videofile.path)

