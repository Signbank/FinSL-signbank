# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from .models import GlossVideo


class HasGlossFilter(admin.SimpleListFilter):
    title = _('Has gloss')
    parameter_name = 'has_gloss'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(gloss__isnull=False)
        if self.value() == 'no':
            return queryset.filter(gloss__isnull=True)


class HasPosterFilter(admin.SimpleListFilter):
    title = _('Has poster')
    parameter_name = 'has_poster'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            # "null=False"
            return queryset.exclude(posterfile='')
        if self.value() == 'no':
            # "null=True"
            return queryset.filter(posterfile='')


class GlossesVideoCountFilter(admin.SimpleListFilter):
    title = _('Gloss has video count of')
    parameter_name = 'gloss_video_count'

    def lookups(self, request, model_admin):
        return (
            ('gt1', _('More than 1')),
            ('gt2', _('More than 2')),
            ('lt2', _('Less than 2')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'gt1':
            # Returns GlossVideos that share the same Gloss.
            gt1 = GlossVideo.objects.values("gloss").annotate(Count("id")).filter(id__count__gt=1).order_by("-id__count")
            queryset = queryset.filter(gloss_id__in=[x["gloss"] for x in gt1])
            return queryset
        if self.value() == 'gt2':
            # Returns GlossVideos of which more that two share the same Gloss.
            gt2 = GlossVideo.objects.values("gloss").annotate(Count("id")).filter(id__count__gt=2).order_by("-id__count")
            queryset = queryset.filter(gloss_id__in=[x["gloss"] for x in gt2])
            return queryset
        if self.value() == 'lt2':
            # Returns GlossVideos that do not share glosses.
            lt2 = GlossVideo.objects.values("gloss").annotate(Count("id")).filter(id__count__lt=2).order_by("-id__count")
            queryset = queryset.filter(gloss_id__in=[x["gloss"] for x in lt2])
            return queryset


class GlossVideoAdmin(admin.ModelAdmin):
    raw_id_fields = ('gloss',)
    fields = ('title', 'videofile', 'posterfile', 'dataset', 'gloss', 'version')
    search_fields = ('^gloss__idgloss', 'videofile', 'title')
    list_display = ('gloss', 'dataset', 'title', 'videofile', 'posterfile', 'id', 'version')
    list_filter = ('gloss__dataset', HasGlossFilter, 'dataset', HasPosterFilter, GlossesVideoCountFilter)

    def get_queryset(self, request):
        qs = super(GlossVideoAdmin, self).get_queryset(request)
        return qs.select_related("gloss", "dataset")


class GlossVideoInline(admin.TabularInline):
    model = GlossVideo
    extra = 1


admin.site.register(GlossVideo, GlossVideoAdmin)
