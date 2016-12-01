from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin as BaseFlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from django_summernote.admin import SummernoteModelAdmin
from modeltranslation.admin import TranslationAdmin


# Adds SummernoteModelAdmin and TranslationAdmin (Modeltranslation), the settings are for Summernote
class FlatPageAdmin(BaseFlatPageAdmin, SummernoteModelAdmin, TranslationAdmin):
    pass

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)