"""Settings for django-modeltranslation. Define the model fields to translate here."""
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions
from .models import Language


class LanguageTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en',)


translator.register(Language, LanguageTranslationOptions)