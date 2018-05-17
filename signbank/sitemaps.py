from django.urls import reverse
from django.contrib import sitemaps
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from .dictionary.models import Gloss


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return ['dictionary:public_gloss_list']

    def location(self, item):
        return reverse(item)


class GlossSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    protocol = 'https'

    def items(self):
        return Gloss.objects.filter(dataset__is_public=True).filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_public_absolute_url()


class SignbankFlatPageSiteMap(FlatPageSitemap):
    changefreq = 'monthly'
    priority = 0.6
    protocol = 'https'

    def lastmod(self, obj):
        ct = ContentType.objects.get_for_model(type(obj))
        print(type(obj))
        return LogEntry.objects.filter(content_type=ct, object_id=obj.id).order_by('-action_time').first().action_time

