from django.contrib import admin
from models import GlossVideo
from .forms import GlossVideoAdminForm
from django.utils.translation import ugettext_lazy as _


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
            return queryset.filter(posterfile__isnull=False)
        if self.value() == 'no':
            return queryset.filter(posterfile__isnull=True)


class GlossVideoAdmin(admin.ModelAdmin):
    fields = ('title', 'videofile', 'posterfile', 'dataset', 'gloss', 'version')
    search_fields = ('^gloss__idgloss',)
    list_display = ('gloss', 'dataset_video', 'title', 'videofile', 'posterfile', 'pk', 'version')
    list_filter = ('gloss__dataset', HasGlossFilter, 'dataset', HasPosterFilter,)
    form = GlossVideoAdminForm

    def dataset_video(self, obj):
        """Get dataset for glossvideo and modify short_description"""
        if obj.dataset:
            return obj.dataset
        return None
    dataset_video.short_description = _("Video's dataset")

admin.site.register(GlossVideo, GlossVideoAdmin)
