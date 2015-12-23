from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import Group
from django.dispatch import receiver
import os


class Page(models.Model):
    # Translators: verbose name for url
    url = models.CharField(_('URL'), max_length=100, db_index=True)
    # Translators: verbose name for title
    title = models.CharField(_('title'), max_length=200)
    # Translators: verbose name for content
    content = models.TextField(_('content'), blank=True)
    # Translators: verbose name for template_name
    template_name = models.CharField(_('template name'), max_length=70, blank=True,
                                     # Translators: help_text for template_name
                                     help_text=_(
                                         "Example: 'pages/contact_page.html'. If this isn't provided, the system will use 'pages/default.html'."))
    # Translators: verbose name for publish
    publish = models.BooleanField(_('publish'),
                                  # # Translators: help_text for publish
                                  help_text=_("If this is checked, the page will be included in the site menus."))
    parent = models.ForeignKey('self', blank=True, null=True,
                               # Translators: help_text for parent
                               help_text=_(
                                   "Leave blank for a top level menu entry.  Top level entries that have sub-pages should be empty as they will not be linked in the menu."))
    index = models.IntegerField(
        # Translators: verbose name for index
        _('ordering index'), default=0,
        # Translators: help_text for index
        help_text=_('Used to order pages in the menu'))
    # Removed null=True from group_required, since django gave a warning that it has no effect on manytomanyfield
    group_required = models.ManyToManyField(Group, blank=True,
                                            # Translators: help_text for group_required
                                            help_text=_(
                                                "This page will only be visible to members of these groups, leave blank to allow anyone to access."))

    class Meta:
        # Translators: verbose name for Page
        verbose_name = _('page')
        # Translators: verbose_name_plural for pages
        verbose_name_plural = _('pages')
        ordering = ('url', 'index')

    def __unicode__(self):
        return u"%s -- %s" % (unicode(self.url), unicode(self.title))

    def get_absolute_url(self):
        return self.url


class PageVideo(models.Model):
    page = models.ForeignKey('Page')
    # Translators: verbose name for PageVideo title
    title = models.CharField(_('title'), max_length=200)
    # Translators: verbose name for PageVideo number
    number = models.PositiveIntegerField(_('number'))
    video = models.FileField(
        upload_to=settings.PAGES_VIDEO_LOCATION, blank=True)

    def __unicode__(self):
        # Translators: __unicode__ return of self (PageVideo)
        return "%s: %s" % (_("Page Video"), self.title,)


def copy_flatpages():
    """Copy existing flatpages into Pages"""

    from django.contrib.flatpages.models import FlatPage

    for fp in FlatPage.objects.all():
        p = Page(url=fp.url, title=fp.title,
                 content=fp.content, publish=False, index=0)
        p.save()

@receiver(models.signals.pre_delete, sender=PageVideo)
def delete_on_delete(sender, instance, **kwargs):
    """On signal delete, use pre_delete to delete the video. This will happen when a PageVideo object is deleted"""
    if instance.video:
        if os.path.isfile(instance.video.path):
            os.remove(instance.video.path)