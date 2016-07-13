from django.contrib import admin
from models import GlossVideo


class GlossVideoAdmin(admin.ModelAdmin):
    search_fields = ['^gloss__idgloss']
    list_display = ['gloss', 'videofile', 'pk', 'version']
    list_filter = ['gloss__dataset']

admin.site.register(GlossVideo, GlossVideoAdmin)
