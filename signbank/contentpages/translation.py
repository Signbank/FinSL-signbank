from modeltranslation.translator import translator, TranslationOptions
from django.contrib.flatpages.models import FlatPage


# This file lists settings for django-modeltranslation.
# Define here which fields from which models you want to add to translation.

class FlatPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content',)


translator.register(FlatPage, FlatPageTranslationOptions)