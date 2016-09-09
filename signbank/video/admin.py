from django.contrib import admin
from models import GlossVideo
from django.utils.translation import ugettext_lazy as _


class GlossVideoAdmin(admin.ModelAdmin):
    search_fields = ('^gloss__idgloss',)
    list_display = ('gloss', 'dataset', 'videofile', 'pk', 'version')
    list_filter = ('gloss__dataset',)

    def dataset(self, obj):
        """Getting the dataset for the glossvideos gloss"""
        return obj.gloss.dataset
    dataset.short_description = _('dataset')


admin.site.register(GlossVideo, GlossVideoAdmin)
