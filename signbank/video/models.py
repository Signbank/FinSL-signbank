# -*- coding: utf-8 -*-
""" Models for the video application keep track of uploaded videos and converted versions"""
from __future__ import unicode_literals

import datetime
import mimetypes
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from storages.backends.s3boto3 import S3Boto3Storage


class GlossVideoStorage(FileSystemStorage):
    """Video storage, handles saving to directories based on filenames first two characters."""

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        super(GlossVideoStorage, self).__init__(location, base_url)

    def get_valid_name(self, name):
        """Generate a valid name, save videos to a 'base_directory', and under it use directories
        named for the first two characters in the filename to partition the videos"""
        base_directory = "glossvideo"
        file_path = os.path.join(name.split("-")[0], name)
        result = os.path.join(base_directory, file_path)
        return result

    def url(self, name):
        return os.path.join(self.base_url, name)


class GlossVideoDynamicStorage(import_string(settings.GLOSS_VIDEO_FILE_STORAGE)):
    def public_url(self, name):
        """ Return the public URL to the object in S3 or local storage.
        This is NOT a presigned URL, use #url for that.
        """
        if isinstance(self, S3Boto3Storage):
            bucket_name = self.bucket.name
            return f'https://{bucket_name}.s3.amazonaws.com/{name}'
        else:
            from django.contrib.sites.models import Site
            domain = Site.objects.get_current().domain
            path = super(GlossVideoDynamicStorage, self).url(name)

            return f'{domain}{path}'

    def set_public(self, name, is_public):
        """ Set the object ACL on the object. This is only supported
        for S3 storage, and is a no-op for local file storage
        """
        if not isinstance(self, S3Boto3Storage):
            return

        self.bucket.meta.client.put_object_acl(
            ACL='public-read' if is_public else 'private',
            Bucket=self.bucket.name,
            Key=name
        )




class GlossVideo(models.Model):
    """A video that represents a particular idgloss"""
    #: Descriptive title of the GlossVideo.
    title = models.CharField(_("Title"), blank=True, unique=False, max_length=100,
                             help_text=_("Descriptive name of the video."))
    #: Video file of the GlossVideo.
    videofile = models.FileField(_("Video file"), storage=GlossVideoDynamicStorage(),
                                 help_text=_("Video file."))
    #: Poster image of the GlossVideo.
    posterfile = models.FileField(_("Poster file"), upload_to=os.path.join("posters"),
                                  storage=GlossVideoDynamicStorage(), blank=True,
                                  help_text=_("Still image representation of the video."), default="")
    #: Boolean: Is this GlossVideo public? Do you want to show it in the public interface, for a published Gloss?
    is_public = models.BooleanField(
        _("Public"), default=True, help_text="Is this video is public or private?")
    #: The Gloss this GlossVideo belongs to.
    gloss = models.ForeignKey('dictionary.Gloss', verbose_name=_("Gloss"), null=True,
                              help_text=_("The gloss this GlossVideo is related to."), on_delete=models.CASCADE)
    #: The Dataset/Lexicon this GlossVideo is part of.
    dataset = models.ForeignKey('dictionary.Dataset', verbose_name=_("Glossvideo dataset"), null=True,
                                help_text=_("Dataset of a GlossVideo, derived from gloss (if any) or chosen when video "
                                            "was uploaded."), on_delete=models.PROTECT)
    # Translators: GlossVideo: version
    #: Version number of the GlossVideo within Glosses videos.
    version = models.IntegerField(_("Version"), default=0,
                                  help_text=_("A number that represents the order of the Glossvideo's in "
                                              "a gloss page. Smaller number means higher priority."))

    #: The type of the video.
    #: When multiple videos are uploaded, we use the type to differentiate
    # which video should be presented in different contexts
    video_type = models.ForeignKey(
        'dictionary.FieldChoice',
        verbose_name=_("Video type"),
        to_field='machine_value',
        help_text=_("The type of video this is for on the gloss"),
        limit_choices_to={'field': 'video_type'},
        null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['version']
        verbose_name = _('Gloss video')
        verbose_name_plural = _('Gloss videos')

    def save(self, *args, **kwargs):
        creating = self._state.adding
        if creating:
            # If no title is set, use the filename of the uploaded file.
            if not self.title:
                self.title = self.videofile.name
            # Set version, one higher than highest version.
            self.version = self.next_version()
            super(GlossVideo, self).save(*args, **kwargs)

        # Rename the videofile if object has gloss set, now that the object has a pk.
        if self.gloss:
            # Make sure glossvideo has the same dataset as gloss.
            self.dataset = self.gloss.dataset
            # Rename videofile.
            self.rename_video()
            # Save without args and kwargs.
            super(GlossVideo, self).save()

    def next_version(self):
        """Return a next suitable version number."""
        try:
            return self.gloss.glossvideo_set.order_by('version').last().version + 1
        except AttributeError:
            # If no GlossVideo.gloss, we can set version to 0.
            return 0

    def get_glosses_videos(self):
        """Returns queryset of glosses GlossVideos."""
        try:
            return self.gloss.glossvideo_set.order_by('version')
        except AttributeError:
            return GlossVideo.objects.none()

    def correct_duplicate_versions(self):
        """If glosses glossvideos have duplicate version numbers, reset version numbers."""
        qs = self.get_glosses_videos()
        version_list = qs.order_by('version').values_list('version', flat=True)
        # Check if version_list has duplicates.
        has_duplicates = len(version_list) != len(set(version_list))
        if has_duplicates:
            # If duplicates, set new version numbers.
            for i, vid in enumerate(qs):
                vid.version = i
                vid.save()
        return

    def move_video_version(self, direction):
        """Move video back or forth in glosses videos."""
        qs = self.get_glosses_videos()
        # First correct possible duplicate version numbers.
        self.correct_duplicate_versions()
        # Exclude self from the queryset.
        glosses_videos = qs.exclude(pk=self.pk)
        if direction == "up" and self.version > 0:
            # Move video "up", make its version lower by swapping with video before it.
            swap_video = glosses_videos.filter(
                version__lte=self.version).last()
            self.version, swap_video.version = swap_video.version, self.version
            self.save(), swap_video.save()
        if direction == "down" and self.version < glosses_videos.last().version:
            # Move video "down", make its version higher by swapping with video after it.
            swap_video = glosses_videos.filter(
                version__gte=self.version).first()
            self.version, swap_video.version = swap_video.version, self.version
            self.save(), swap_video.save()
        return

    def get_absolute_url(self):
        return self.videofile.url

    def rename_video(self):
        """Rename the video and move the video to correct path if the glossvideo object has a foreignkey to a gloss."""
        storage = self.videofile.storage
        # Do not rename the file if glossvideo doesn't have a gloss.
        if hasattr(self, 'gloss') and self.gloss is not None:
            # Store the old file path, needed for removal later.
            old_file = self.videofile
            # Create the base filename.
            new_filename = self.create_filename()
            # Get the relative path in media folder.
            full_new_path = storage.get_valid_name(new_filename)
            # Proceed to change the file path if the new path is not equal to old path.
            if not self.videofile.storage.exists(full_new_path):
                # Save the file into the new path.
                saved_file_path = storage.save(full_new_path, old_file)
                # Set the actual file path to videofile.
                self.videofile = saved_file_path

                old_file.storage.delete(old_file.path)

    def create_filename(self):
        """Returns a correctly named filename"""
        return "{glosspk}-{idgloss}_{videotype}_{pk}{ext}".format(
            idgloss=self.gloss.idgloss,
            glosspk=self.gloss.pk,
            videotype=self.video_type.english_name if self.video_type else "unknown",
            ext=self.get_extension(),
            pk=self.pk
        )

    def create_poster_filename(self, ext):
        """Returns a preferred filename of posterfile. Ext is the file extension without the dot."""
        if self.gloss:
            return "{idgloss}-{glosspk}_{videotype}_{pk}.{ext}".format(
                idgloss=self.gloss.idgloss,
                glosspk=self.gloss.pk,
                videotype=self.video_type.english_name if self.video_type else "unknown",
                pk=self.pk,
                ext=ext
            )
        return "{videofilename}.{ext}".format(videofilename=self.videofile.name, ext=ext)

    @staticmethod
    def rename_glosses_videos(gloss):
        """Renames the filenames of selected Glosses videos to match the Gloss name"""
        glossvideos = gloss.glossvideo_set.all().order_by('version')
        for glossvideo in glossvideos:
            glossvideo.save()

    def get_extension(self):
        """Returns videofiles extension."""
        return os.path.splitext(self.videofile.name)[1]

    def get_content_type(self):
        """ Returns the (guessed) mimetype of the videofile"""
        content_type, encoding = mimetypes.guess_type(self.videofile.name)

        return content_type

    def is_image(self):
        return self.get_content_type().startswith("image/")

    def is_video(self):
        return self.get_content_type().startswith("video/")

    def set_public(self, is_public):
        self.is_public = is_public
        self.save()
        self.videofile.storage.set_public(self.videofile.name, is_public)

        True

    def has_poster(self):
        """Returns true if the glossvideo has a poster file."""
        if self.posterfile:
            return True
        return False

    def get_videofile_modified_date(self):
        """Return a Datetime object from filesystems last modified time of path."""
        try:
            return self.videofile.storage.get_modified_time(self.videofile.name)
        except:
            return None

    def __str__(self):
        return self.videofile.name
