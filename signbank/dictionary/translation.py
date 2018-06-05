# -*- coding: utf-8 -*-
"""Settings for django-modeltranslation. Define the model fields to translate here."""
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions
from .models import Dataset, Language, SignLanguage


class DatasetTranslationOptions(TranslationOptions):
    fields = ('public_name', 'description', 'copyright',)


class LanguageTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en',)


class SignLanguageTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en',)


translator.register(Dataset, DatasetTranslationOptions)
translator.register(Language, LanguageTranslationOptions)
translator.register(SignLanguage, SignLanguageTranslationOptions)