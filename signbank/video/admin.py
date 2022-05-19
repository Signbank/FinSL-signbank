# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _lazy

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


def set_public(modeladmin, request, queryset):
    queryset.update(is_public=True)


def set_hidden(modeladmin, request, queryset):
    queryset.update(is_public=False)


set_public.short_description = _lazy("Set selected videos public")
set_hidden.short_description = _lazy("Set selected videos hidden")


class GlossVideoAdmin(admin.ModelAdmin):
    raw_id_fields = ('gloss',)
    fields = ('is_public', 'title', 'videofile', 'posterfile',
              'dataset', 'gloss', 'video_type', 'version')
    search_fields = ('^gloss__idgloss', 'videofile', 'title')
    list_display = ('gloss', 'is_public', 'dataset', 'title',
                    'videofile', 'video_type', 'posterfile', 'id', 'version')
    list_filter = ('is_public', 'video_type', 'gloss__dataset',
                   HasGlossFilter, 'dataset', HasPosterFilter, GlossesVideoCountFilter)
    actions = [set_public, set_hidden]

    def get_queryset(self, request):
        qs = super(GlossVideoAdmin, self).get_queryset(request)
        return qs.select_related("gloss", "video_type", "dataset")


class GlossVideoInline(admin.TabularInline):
    model = GlossVideo
    extra = 0


admin.site.register(GlossVideo, GlossVideoAdmin)
