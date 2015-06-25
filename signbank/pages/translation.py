from modeltranslation.translator import translator, TranslationOptions
from signbank.pages.models import Page

# This file lists settings for django-modeltranslation.
# Define here which fields from which models you want to add to translation.

class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'content',)

translator.register(Page, PageTranslationOptions)