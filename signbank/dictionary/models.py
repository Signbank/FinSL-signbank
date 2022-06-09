# -*- coding: utf-8 -*-
"""Models for the Signbank dictionary/corpus."""
from __future__ import unicode_literals

import json
import re
from collections import OrderedDict
from itertools import groupby

import reversion
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError, models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from tagging.models import Tag
from tagging.registry import AlreadyRegistered
from tagging.registry import register as tagging_register


@python_2_unicode_compatible
class Dataset(models.Model):
    """Dataset/Lexicon of which Glosses are part of."""
    #: A private name for the Dataset. Can include abbrevations not recognizable by the general users.
    name = models.CharField(_("Name"), unique=True,
                            blank=False, null=False, max_length=60)
    #: Public name for the Dataset, intended for users of the public interface.
    public_name = models.CharField(_("Public name"), max_length=60)
    #: Boolean defining whether to show this Dataset in the public interface.
    is_public = models.BooleanField(_("Is public"), default=False, help_text=_(
        "Is this dataset is public or private?"))
    #: The Sign Language of the Glosses in this Dataset.
    signlanguage = models.ForeignKey("SignLanguage", verbose_name=_(
        "Sign language"), on_delete=models.PROTECT)
    #: The translation equivalent languages that should be available to the Glosses of this Dataset.
    translation_languages = models.ManyToManyField("Language", verbose_name=_("Translation equivalent languages"),
                                                   help_text=_("These languages are options for translation equivalents."))
    #: A description of the Dataset: who maintains it, what is its purpose, etc.
    description = models.TextField(_("Description"))
    #: The copyright statement for the data in this Dataset, the license used for the videos etc.
    copyright = models.TextField(_("Copyright"))
    #: The admins of this Dataset. Admins receive notifications when a user applies for permissins for the Dataset.
    admins = models.ManyToManyField(User, verbose_name=_("Admins"))

    class Meta:
        permissions = (
            ('access_dataset', _('Access dataset')),
        )
        verbose_name = _('Lexicon')
        verbose_name_plural = _('Lexicons')
        ordering = ['id', ]

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class GlossTranslations(models.Model):
    """Store a string representation of translation equivalents of certain Language for a Gloss."""
    #: The Gloss to translate
    gloss = models.ForeignKey("Gloss", verbose_name=_(
        "Gloss"), on_delete=models.CASCADE)
    #: The written/spoken Language of the translations.
    language = models.ForeignKey("Language", verbose_name=_(
        "Language"), on_delete=models.CASCADE)
    #: The fields that contains the translations, a text field.
    translations = models.TextField(blank=True)
    #: The fields that contains the secondary translations, a text field.
    translations_secondary = models.TextField(blank=True, null=True)
    #: The fields that contains the minor translations, a text field.
    translations_minor = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (("gloss", "language"),)
        verbose_name = _('Gloss translation field')
        verbose_name_plural = _('Gloss translation fields')
        ordering = ['language']

    def save(self, *args, **kwargs):
        if self.translations == ' ':
            self.translations = None

        if self.translations_secondary == ' ':
            self.translations_secondary = None

        if self.translations_minor == ' ':
            self.translations_minor = None

        # Is the object being created
        creating = self._state.adding
        # Remove duplicates and keep the order.
        keywords = self.get_keywords_unique()

        # Get Translation objects for GlossTranslation.gloss, filter according to GlossTranslation.language
        translations = self.gloss.translation_set.filter(
            language=self.language)
        # Keep the translation objects that have the Keywords that remain.
        translations_to_keep = translations.filter(
            keyword__text__in=keywords, language=self.language)
        # Delete translations that no longer exist in field GlossTranslations.translations.
        translations.exclude(pk__in=translations_to_keep).delete()

        if not keywords or (len(keywords) < 2 and keywords[0].strip() == ""):
            # If the to be saved object has no 'translations'
            if not creating:
                # If the object is being updated
                self.delete()
            # If object is being created with empty 'translations', don't save.
            return

        existing_keywords = Keyword.objects.filter(text__in=keywords)
        for i, keyword_text in enumerate(keywords):
            (keyword, created) = existing_keywords.get_or_create(text=keyword_text)
            try:
                translation = translations_to_keep.get(
                    gloss=self.gloss, language=self.language, keyword=keyword)
            except Translation.DoesNotExist:
                translation = Translation(
                    gloss=self.gloss, language=self.language, keyword=keyword)
            translation.order = i
            translation.save()

        super(GlossTranslations, self).save(*args, **kwargs)

    def get_keywords(self):
        """Returns keywords parsed from self.translations."""
        all_translations_cleaned = ''

        # Remove number(s) that end with a dot (e.g. '1.') from the 'value'.
        if self.translations:
            translations_cleaned = re.sub('\d\.', '', str(self.translations))
            all_translations_cleaned += translations_cleaned

        if self.translations_secondary:
            translations_cleaned_secondary = re.sub(
                '\d\.', '', str(self.translations_secondary))
            all_translations_cleaned += ','
            all_translations_cleaned += translations_cleaned_secondary

        if self.translations_minor:
            translations_cleaned_minor = re.sub(
                '\d\.', '', str(self.translations_minor))
            all_translations_cleaned += ','
            all_translations_cleaned += translations_cleaned_minor

        # Splitting the remaining string on comma, dot or semicolon. Then strip spaces around the keyword(s).
        keywords = [k.strip() for k in re.split(
            '[,.;]', all_translations_cleaned)]

        if '' in keywords:
            keywords.remove('')

        return keywords

    def get_keywords_unique(self):
        """Returns only unique keywords from get_keywords()"""
        return list(OrderedDict.fromkeys(self.get_keywords()))

    def has_duplicates(self):
        keywords_str = self.get_keywords()
        return len(keywords_str) != (len(set(keywords_str)))


@python_2_unicode_compatible
@reversion.register()
class Translation(models.Model):
    """A translation equivalent of a sign in selected language."""
    #: The Gloss to translate.
    gloss = models.ForeignKey("Gloss", verbose_name=_(
        "Gloss"), on_delete=models.CASCADE)
    #: The written/spoken Language of the translation.
    language = models.ForeignKey("Language", verbose_name=_(
        "Language"), on_delete=models.CASCADE)
    #: The Keyword of the translation, the textual form.
    keyword = models.ForeignKey("Keyword", verbose_name=_(
        "Keyword"), on_delete=models.PROTECT)
    #: The order number of the Translation within a Glosses Translations.
    order = models.IntegerField("Order")

    class Meta:
        unique_together = (("gloss", "language", "keyword"),)
        ordering = ['gloss', 'language', 'order']
        verbose_name = _('Translation equivalent')
        verbose_name_plural = _('Translation equivalents')

    def __str__(self):
        return self.keyword.text


@python_2_unicode_compatible
@reversion.register()
class Keyword(models.Model):
    """A keyword that stores the text for translation(s)"""
    #: The text of a Keyword.
    text = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['text']
        verbose_name = _('Keyword')
        verbose_name_plural = _('Keywords')

    class Admin:
        search_fields = ['text']

    def __str__(self):
        return self.text


@python_2_unicode_compatible
class Language(models.Model):
    """A written language, used for translations in written languages."""
    #: The name of a spoken/written Language.
    name = models.CharField(max_length=50)
    #: The ISO 639-1 code of the Language (2 characters long).
    language_code_2char = models.CharField(unique=False, blank=False, null=False, max_length=2, help_text=_(
        """ISO 639-1 language code (2 characters long) of a written language."""))
    #: The ISO 639-3 code of the Language (3 characters long).
    language_code_3char = models.CharField(unique=False, blank=False, null=False, max_length=3, help_text=_(
        """ISO 639-3 language code (3 characters long) of a written language."""))
    #: Description of the Language.
    description = models.TextField()

    class Meta:
        ordering = ['name']
        verbose_name = _('Written language')
        verbose_name_plural = _('Written languages')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class SignLanguage(models.Model):
    """A sign language."""
    #: The name of the Sign Language
    name = models.CharField(max_length=50)
    #: The ISO 639-3 code of the Sign Language (3 characters long).
    language_code_3char = models.CharField(unique=False, blank=False, null=False, max_length=3, help_text=_(
        """ISO 639-3 language code (3 characters long) of a sign language."""))

    class Meta:
        ordering = ['name']
        verbose_name = _('Sign language')
        verbose_name_plural = _('Sign languages')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Dialect(models.Model):
    """A dialect name - a regional dialect of a given Language"""
    #: The Language of the Dialect.
    language = models.ForeignKey("SignLanguage", verbose_name=_(
        "Sign language"), on_delete=models.CASCADE)
    #: Name of the Dialect.
    name = models.CharField(max_length=50)
    #: Description of the Dialect.
    description = models.TextField()

    class Meta:
        ordering = ['language', 'name']
        verbose_name = _('Dialect')
        verbose_name_plural = _('Dialects')

    def __str__(self):
        return str(self.language.name) + "/" + str(self.name)


@python_2_unicode_compatible
class RelationToForeignSign(models.Model):
    """Defines a relationship to another sign in another language (often a loan)"""
    #: The source Gloss of the relation.
    gloss = models.ForeignKey("Gloss", on_delete=models.CASCADE)
    # Translators: RelationToForeignSign field verbose name
    #: Boolean: Is this a loan sign?
    loan = models.BooleanField(_("Loan Sign"), default=False)
    # Translators: RelationToForeignSign field verbose name
    #: The language of the related sign.
    other_lang = models.CharField(_("Related Language"), max_length=20)
    # Translators: RelationToForeignSign field verbose name
    #: The name of the Gloss in the related language.
    other_lang_gloss = models.CharField(
        _("Gloss in related language"), max_length=50)

    class Meta:
        ordering = ['gloss', 'loan', 'other_lang', 'other_lang_gloss']
        verbose_name = _('Relation to Foreign Sign')
        verbose_name_plural = _('Relations to Foreign Signs')

    class Admin:
        list_display = ['gloss', 'loan', 'other_lang', 'other_lang_gloss']
        list_filter = ['other_lang']
        search_fields = ['gloss__idgloss']

    def __str__(self):
        return str(self.gloss) + "/" + str(self.other_lang) + ',' + str(self.other_lang_gloss)


@python_2_unicode_compatible
class FieldChoice(models.Model):
    #: The name of the FieldChoice.
    field = models.CharField(max_length=50)
    #: English (verbose) name of the FieldChoice.
    english_name = models.CharField(max_length=50)
    #: Machine value of the FieldChoice, its ID number.
    machine_value = models.IntegerField(unique=True)

    def __str__(self):
        # return self.field + ': ' + self.english_name + ' (' + str(self.machine_value) + ')'
        return self.english_name

    class Meta:
        ordering = ['field', 'machine_value']
        verbose_name = _('Field choice')
        verbose_name_plural = _('Field choices')


def build_choice_list(field):
    """This function builds a list of choices from FieldChoice."""
    # TODO: This is probably no longer needed, remove its usage if possible.
    choice_list = []
    # Get choices for a certain field in FieldChoices, append machine_value and english_name
    try:
        for choice in FieldChoice.objects.filter(field=field):
            choice_list.append(
                (str(choice.machine_value), choice.english_name))

        return choice_list
    # Enter this exception if for example the db has no data yet (without this it is impossible to migrate)
    except OperationalError:
        return choice_list


@python_2_unicode_compatible
class Gloss(models.Model):
    class Meta:
        unique_together = (("idgloss", "dataset"),)
        verbose_name = _('Gloss')
        verbose_name_plural = _('Glosses')
        ordering = ['idgloss']
        permissions = (
            # Translators: Gloss permissions
            ('update_video', _("Can Update Video")),
            # Translators: Gloss permissions
            ('search_gloss', _('Can Search/View Full Gloss Details')),
            # Translators: Gloss permissions
            ('export_csv', _('Can export sign details as CSV')),
            ('import_csv', _('Can import glosses from a CSV file')),
            # Translators: Gloss permissions
            ('view_advanced_properties', _(
                'Include all properties in sign detail view')),
            # Translators: Gloss permissions
            ('publish_gloss', _('Can publish and unpublish Glosses')),
        )
    # ### Fields ###
    id = models.AutoField(auto_created=True, primary_key=True,
                          serialize=False, verbose_name='Sign number')
    #: Boolean: Is this Gloss published in the public interface?
    published = models.BooleanField(_("Published"), default=False,
                                    help_text=_("Publish this gloss in the public gloss list"))
    #: Boolean: Exclude this gloss from all ELAN externally controlled vocabularies (ECV)?
    exclude_from_ecv = models.BooleanField(_("Exclude from ECV"), default=False,
                                           help_text=_("Exclude from ELAN externally controlled vocabularies (ECV)"))
    #: The Dataset (Lexicon) this Gloss is part of.
    dataset = models.ForeignKey("Dataset", verbose_name=_("Glosses dataset"),
                                help_text=_("Dataset a gloss is part of"), on_delete=models.PROTECT)
    # Translators: Gloss field: idgloss, verbose name
    #: Gloss in Finnish. This is the unique identifying name of the Gloss.
    idgloss = models.CharField(_("Gloss"), max_length=60,
                               # Translators: Help text for Gloss field: idgloss
                               help_text=_("""This is the unique identifying name of a Gloss."""))
    # Translators: Gloss field: idgloss_mi (english), verbose name
    #: Gloss in Māori. This is the Māori name of the Gloss.
    idgloss_mi = models.CharField(_("Gloss in Māori"), blank=True, null=True, max_length=150,
                                  # Translators: Help text for Gloss field: idgloss_mi (maori)
                                  help_text=_("""This is the Māori name for the Gloss"""))
    # Translators: Gloss field: idgloss_mi (maori), verbose name
   # Translators: Gloss models field: notes, verbose name. Notes/Further information about a Gloss.
    #: Notes about the Gloss.
    notes = models.TextField(_("Notes"), blank=True)

    #: One or more regional dialects that this Gloss is used in.
    dialect = models.ManyToManyField(Dialect, blank=True)

    #: The DateTime when the Gloss was created.
    created_at = models.DateTimeField(auto_now_add=True)
    #: The User who created the Gloss.
    created_by = models.ForeignKey(
        User, related_name='created_by_user', null=True, on_delete=models.SET_NULL)
    #: The DateTime when the Glosses information was last updated.
    updated_at = models.DateTimeField(auto_now=True)
    #: The User who last updated the Glosses information.
    updated_by = models.ForeignKey(
        User, related_name='updated_by_user', null=True, on_delete=models.SET_NULL)

    # ### Phonology fields ###
    # Translators: Gloss models field: handedness, verbose name
    handedness = models.ForeignKey('FieldChoice', verbose_name=_("Handedness"), to_field='machine_value',
                                   db_column='handedness', limit_choices_to={'field': 'handedness'},
                                   related_name="handedness", blank=True, null=True, on_delete=models.SET_NULL)
    # Translators: Gloss models field: strong_handshape, verbose name
    strong_handshape = models.ForeignKey('FieldChoice', verbose_name=_("Strong Hand"), to_field='machine_value',
                                         db_column='strong_handshape', limit_choices_to={'field': 'strong_handshape'},
                                         related_name="strong_handshape", blank=True, null=True, on_delete=models.SET_NULL)

    # Translators: Gloss models field: weak_handshape, verbose name
    weak_handshape = models.ForeignKey('FieldChoice', verbose_name=_("Weak Hand"), to_field='machine_value',
                                       db_column='weak_handshape', limit_choices_to={'field': 'weak_handshape'},
                                       related_name="weak_handshape", blank=True, null=True, on_delete=models.SET_NULL)

    # Translators: Gloss models field: location, verbose name
    location = models.ForeignKey('FieldChoice', verbose_name=_("Location"), to_field='machine_value',
                                 db_column='location', limit_choices_to={'field': 'location'}, related_name="location",
                                 blank=True, null=True, on_delete=models.SET_NULL)

    # Translators: Gloss models field: relation_between_articulators, verbose name
    relation_between_articulators = models.ForeignKey('FieldChoice', verbose_name=_("Relation Between Articulators"),
                                                      to_field='machine_value',
                                                      db_column='relation_between_articulators',
                                                      limit_choices_to={
                                                          'field': 'relation_between_articulators'},
                                                      related_name="relation_between_articulators", blank=True,
                                                      null=True, on_delete=models.SET_NULL)

    # Translators: Gloss models field: absolute_orientation_palm, verbose name
    absolute_orientation_palm = models.ForeignKey('FieldChoice', verbose_name=_("Absolute Orientation: Palm"),
                                                  to_field='machine_value', db_column='absolute_orientation_palm',
                                                  limit_choices_to={
                                                      'field': 'absolute_orientation_palm'},
                                                  related_name="absolute_orientation_palm", blank=True, null=True,
                                                  on_delete=models.SET_NULL)
    # Translators: Gloss models field: absolute_orientation_fingers, verbose name
    absolute_orientation_fingers = models.ForeignKey('FieldChoice', verbose_name=_("Absolute Orientation: Fingers"),
                                                     to_field='machine_value', db_column='absolute_orientation_fingers',
                                                     limit_choices_to={
                                                         'field': 'absolute_orientation_fingers'},
                                                     related_name="absolute_orientation_fingers", blank=True, null=True,
                                                     on_delete=models.SET_NULL)

    # Translators: Gloss models field: relative_orientation_movement, verbose name
    relative_orientation_movement = models.ForeignKey('FieldChoice', verbose_name=_("Relative Orientation: Movement"),
                                                      to_field='machine_value',
                                                      db_column='relative_orientation_movement',
                                                      limit_choices_to={
                                                          'field': 'relative_orientation_movement'},
                                                      related_name="relative_orientation_movement", blank=True,
                                                      null=True, on_delete=models.SET_NULL)
    # Translators: Gloss models field: relative_orientation_location, verbose name
    relative_orientation_location = models.ForeignKey('FieldChoice', verbose_name=_("Relative Orientation: Location"),
                                                      to_field='machine_value',
                                                      db_column='relative_orientation_location',
                                                      limit_choices_to={
                                                          'field': 'relative_orientation_location'},
                                                      related_name="relative_orientation_location", blank=True,
                                                      null=True, on_delete=models.SET_NULL)
    # Translators: Gloss models field: orientation_change, verbose name
    orientation_change = models.ForeignKey('FieldChoice', verbose_name=_("Orientation Change"),
                                           to_field='machine_value', db_column='orientation_change',
                                           limit_choices_to={
                                               'field': 'orientation_change'},
                                           related_name="orientation_change", blank=True, null=True, on_delete=models.SET_NULL)

    # Translators: Gloss models field: handshape_change, verbose name
    handshape_change = models.ForeignKey('FieldChoice', verbose_name=_("Handshape Change"), to_field='machine_value',
                                         db_column='handshape_change', limit_choices_to={'field': 'handshape_change'},
                                         related_name="handshape_change", blank=True, null=True, on_delete=models.SET_NULL)

    # Translators: Gloss models field: repeated_movement, verbose name
    repeated_movement = models.NullBooleanField(
        _("Repeated Movement"), null=True, default=False)
    # Translators: Gloss models field: alternating_movement, verbose name
    alternating_movement = models.NullBooleanField(
        _("Alternating Movement"), null=True, default=False)

    # Translators: Gloss models field: movement_shape, verbose name
    movement_shape = models.ForeignKey('FieldChoice', verbose_name=_("Movement Shape"), to_field='machine_value',
                                       db_column='movement_shape', limit_choices_to={'field': 'movement_shape'},
                                       related_name="movement_shape", blank=True, null=True, on_delete=models.SET_NULL)
    # Translators: Gloss models field: movement_direction, verbose name
    movement_direction = models.ForeignKey('FieldChoice', verbose_name=_("Movement Direction"),
                                           to_field='machine_value', db_column='movement_direction',
                                           limit_choices_to={
                                               'field': 'movement_direction'},
                                           related_name="movement_direction", blank=True, null=True, on_delete=models.SET_NULL)
    # Translators: Gloss models field: movement_manner, verbose name
    movement_manner = models.ForeignKey('FieldChoice', verbose_name=_("Movement Manner"), to_field='machine_value',
                                        db_column='movement_manner', limit_choices_to={'field': 'movement_manner'},
                                        related_name="movement_manner", blank=True, null=True, on_delete=models.SET_NULL)
    # Translators: Gloss models field: contact_type, verbose name
    contact_type = models.ForeignKey('FieldChoice', verbose_name=_("Contact Type"), to_field='machine_value',
                                     db_column='contact_type', limit_choices_to={'field': 'contact_type'},
                                     related_name="contact_type", blank=True, null=True, on_delete=models.SET_NULL)

    # Translators: Gloss models field: phonology_other verbose name
    phonology_other = models.TextField(
        _("Phonology Other"), null=True, blank=True)

    # Translators: Gloss models field: mouth_gesture, verbose name
    mouth_gesture = models.CharField(
        _("Mouth Gesture"), max_length=50, blank=True)
    # Translators: Gloss models field: mouthing, verbose name
    mouthing = models.CharField(_("Mouthing"), max_length=50, blank=True)
    # Translators: Gloss models field: phonetic_variation, verbose name
    phonetic_variation = models.CharField(
        _("Phonetic Variation"), max_length=50, blank=True, )

    wordclasses = models.ManyToManyField('FieldChoice', verbose_name=_(
        "Wordclasses"), limit_choices_to={'field': 'wordclass'}, related_name='wordclass_glosses')

    usage = models.ManyToManyField('FieldChoice', verbose_name=_(
        "Usage"), limit_choices_to={'field': 'usage'}, related_name='usage_glosses')

    # ### Semantic fields
    # Translators: Gloss models field: iconic_image, verbose name
    iconic_image = models.CharField(
        _("Iconic Image"), max_length=50, blank=True)
    # Translators: Gloss models field: named_entity, verbose name
    named_entity = models.ForeignKey('FieldChoice', verbose_name=_("Named Entity"), to_field='machine_value',
                                     db_column='named_entity', limit_choices_to={'field': 'named_entity'},
                                     related_name="named_entity", blank=True, null=True, on_delete=models.SET_NULL)
    # Translators: Gloss models field: semantic_field, verbose name
    semantic_field = models.ForeignKey('FieldChoice', verbose_name=_("Semantic Field"), to_field='machine_value',
                                       db_column='semantic_field', limit_choices_to={'field': 'semantic_field'},
                                       related_name="semantic_field", blank=True, null=True, on_delete=models.SET_NULL)

    # ### Frequency fields
    # Translators: Gloss models field_ number_of_occurences, verbose name
    number_of_occurences = models.IntegerField(
        _("Number of Occurrences"), null=True, blank=True,
        # Translators: Help text for Gloss models field: number_of_occurences
        help_text=_("Number of occurences in annotation materials"))

    #: Hints are aids for hearing learners of NZSL to help them to produce or remember the Gloss.
    hint = models.TextField(_("Hint"), null=True, blank=True)

    #: The signer of this Gloss.
    signer = models.ForeignKey("Signer", null=True, blank=True, verbose_name=_("Signer"),
                               help_text=_("Signer for the Gloss"), on_delete=models.PROTECT)

    #: Adding filmbatch which holds records of which 'batch' of recordings the video is from.
    filmbatch = models.CharField(max_length=150, null=True, blank=True,
                                 help_text="Which batch of recordings the video is from")

    #: Store example content for this sign. This is in two forms:
    # videoexample[1-4]: The literal translation, annotated with gloss IDs when a gloss is used,
    #                    as well as editorial annotations.
    # videoexample[1-4]translation: The translated example sentence in English. This column is
    #                               natural language and is not annotated.
    # In the future, this should be combined in some way with glossvideo so that these examples
    # sit directly alongside, or on a glossvideo.
    videoexample1 = models.CharField(_("Example video 1 glossing"),
                                     max_length=255, null=True, blank=True, help_text="Glossing for video example 1")
    videoexample2 = models.CharField(_("Example video 2 glossing"),
                                     max_length=255, null=True, blank=True, help_text="Glossing for video example 2")
    videoexample3 = models.CharField(_("Example video 3 glossing"),
                                     max_length=255, null=True, blank=True, help_text="Glossing for video example 3")
    videoexample4 = models.CharField(_("Example video 4 glossing"),
                                     max_length=255, null=True, blank=True, help_text="Glossing for video example 4")

    videoexample1_translation = models.CharField(_("Example video 1 English translation"),
                                                 max_length=255, null=True, blank=True, help_text="English translation for video example 1")
    videoexample2_translation = models.CharField(_("Example video 2 English translation"),
                                                 max_length=255, null=True, blank=True, help_text="English translation for video example 2")
    videoexample3_translation = models.CharField(_("Example video 3 English translation"),
                                                 max_length=255, null=True, blank=True, help_text="English translation for video example 3")
    videoexample4_translation = models.CharField(_("Example video 4 English translation"),
                                                 max_length=255, null=True, blank=True, help_text="English translation for video example 4")

    # concise - boolean indicating gloss is included in print 2002 Concise Dictionary of NZSL.
    concise = models.BooleanField(_("Concise"), default=False, choices=[(True, 'Yes'), (False, 'No')],
                                     help_text=_("Was this gloss included in print 2002 Concise Dictionary of NZSL?"))

    fingerspelling = models.BooleanField(_("Fingerspelling"), default=False, help_text=_("Does the sign contain fingerspelling?"),
                        null = False, blank = False, choices = [(True, 'Yes'), (False, 'No')])
    # inflections - booleans labelled (1)"temporal", (2)"manner and degree", (3)"pluralisation"
    inflection_temporal = models.BooleanField(_("Inflection: Temporal"), default=False, choices=[(True, 'Yes'), (False, 'No')],
                                    help_text=_("Can the sign have a temporal inflection?’"))
    inflection_manner_degree = models.BooleanField(_("Inflection: Manner and Degree"), default=False, choices=[(True, 'Yes'), (False, 'No')],
                                    help_text=_("Can the sign be inflected for manner and degree?"))
    inflection_plural = models.BooleanField(_("Inflection: Pluralisation"), default=False, choices=[(True, 'Yes'), (False, 'No')],
                                    help_text=_("Can the sign have a plural inflection?"))
    one_or_two_hand = models.BooleanField(
        _("One or two hands"), default=False, null=False, blank=False, choices=[(True, 'Yes'), (False, 'No')])
    number_incorporated = models.BooleanField(
        _("Number incorporated"), default=False, blank=False, null=False, choices=[(True, 'Yes'), (False, 'No')])
    locatable = models.BooleanField(_("Locatable"), default=False, null=False, blank=False, choices=[
                                    (True, 'Yes'), (False, 'No')])
    directional = models.BooleanField(_("Directional"),
                                      default=False, null=False, blank=False, choices=[(True, 'Yes'), (False, 'No')])

    # age_variation: 'none', 'older', or 'younger'
    age_variation = models.ForeignKey('FieldChoice', verbose_name=_("Age variation"), to_field='machine_value',
                                       db_column='age_variation', limit_choices_to={'field': 'age_variation'},
                                       related_name="age_variation", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.idgloss

    def get_absolute_url(self):
        return self.get_admin_absolute_url()

    def get_admin_absolute_url(self):
        return reverse('dictionary:admin_gloss_view', args=[str(self.id)])

    def get_public_absolute_url(self):
        return reverse('dictionary:public_gloss_view', args=[str(self.id)])

    def field_labels(self):
        """Return the dictionary of field labels for use in a template"""
        d = dict()
        for f in self._meta.fields:
            d[f.name] = self._meta.get_field(f.name).verbose_name

        return d

    def get_translation_languages(self):
        """Returns translation languages that are set for the Dataset of the Gloss."""
        return self.dataset.translation_languages.all()

    def get_translations_for_translation_languages(self):
        """Returns a zipped list of translation languages and translations."""
        translation_list = []
        translation_languages = self.get_translation_languages()
        for language in translation_languages:
            try:
                # Get translations from GlossTranslation object, if it exists for gloss+language.
                translation_list.append(GlossTranslations.objects.get(
                    gloss=self, language=language))
            except GlossTranslations.DoesNotExist:
                # If it doesn't exist, try to get translations from Translation objects.
                translations = Translation.objects.filter(
                    gloss=self, language=language)
                kwd_str = ""
                first = True
                for trans in translations:
                    if first:
                        kwd_str += str(trans.keyword)
                        first = False
                    else:
                        kwd_str += ", " + trans.keyword.text
                translation_list.append(kwd_str)

        return list(zip(translation_languages, translation_list))

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Gloss._meta.fields]

    @staticmethod
    def get_choice_lists():
        """Return FieldChoices for selected fields in JSON, grouped by field, key = machine_value, value = english_name"""
        # The fields we want to generate choice lists for
        fields = ['handedness', 'location', 'strong_handshape', 'weak_handshape',
                  'relation_between_articulators', 'absolute_orientation_palm', 'absolute_orientation_fingers',
                  'relative_orientation_movement', 'relative_orientation_location', 'handshape_change',
                  'repeated_movement', 'alternating_movement', 'movement_shape', 'movement_direction',
                  'movement_manner', 'contact_type', 'named_entity', 'orientation_change', 'semantic_field',
                  'video_type', 'wordclass', 'fingerspelling', 'usage',
                  'age_variation']

        qs = FieldChoice.objects.filter(field__in=fields).values(
            'field', 'machine_value', 'english_name')
        # TODO: How about other fields like Morphology? Should we just get all the fields?
        # Group the values by 'field'
        fields_grouped = {k: list(v) for k, v in groupby(
            qs, key=lambda x: x["field"])}
        field_choices = dict()
        # Construct a dict that has 'machine_value' as key and 'english_name' as value.
        for k, v in fields_grouped.items():
            field_choices[k] = {
                x['machine_value']: str(x['english_name']) for x in v}

        return field_choices


@python_2_unicode_compatible
class GlossURL(models.Model):
    """URL's for gloss"""
    #: The Gloss the URL belongs to.
    gloss = models.ForeignKey("Gloss", verbose_name=_(
        "Gloss"), on_delete=models.CASCADE)
    #: The URL, a websites address.
    url = models.URLField(max_length=200)

    class Meta:
        verbose_name = _('Gloss URL')
        verbose_name_plural = _('Gloss URLs')

    def __str__(self):
        return self.gloss.idgloss + " - " + self.url


@python_2_unicode_compatible
class AllowedTags(models.Model):
    """Tags a model is allowed to use."""
    #: The tags that are shown in tag lists.
    allowed_tags = models.ManyToManyField(Tag, verbose_name=_("Allowed tags"))
    #: The ContentType of the object whose AllowedTags we set.
    content_type = models.OneToOneField(ContentType, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Allowed tags')
        verbose_name_plural = _('Allowed tags')

    def __str__(self):
        return str(self.content_type)


@python_2_unicode_compatible
class GlossRelation(models.Model):
    """Relation between two glosses"""
    #: The source Gloss of the Relation.
    source = models.ForeignKey(
        Gloss, related_name="glossrelation_source", on_delete=models.CASCADE)
    #: The target Gloss of the Relation, the Gloss to which the source Gloss related to.
    target = models.ForeignKey(
        Gloss, related_name="glossrelation_target", on_delete=models.CASCADE)

    def tag(self):
        """The type of the Relation, a Tag."""
        return list(Tag.objects.get_for_object(self))
    tag.short_description = 'Relation type'

    class Meta:
        ordering = ['source']
        verbose_name = _('Gloss relation')
        verbose_name_plural = _('Gloss relations')

    def __str__(self):
        return str(self.target)


@python_2_unicode_compatible
class Relation(models.Model):  # TODO: Remove
    """A relation between two glosses"""
    source = models.ForeignKey(
        Gloss, related_name="relation_sources", on_delete=models.CASCADE)
    target = models.ForeignKey(
        Gloss, related_name="relation_targets", on_delete=models.CASCADE)
    # role = models.CharField(max_length=20, choices=build_choice_list('MorphologyType'))
    role = models.ForeignKey('FieldChoice', to_field='machine_value', db_column='MorphologyType',
                             limit_choices_to={'field': 'MorphologyType'}, blank=True, on_delete=models.CASCADE)
    # antonym, synonym, cf (what's this? - see also), var[b-f]
    # (what's this - variant (XXXa is the stem, XXXb is a variant)

    class Admin:
        list_display = ['source', 'role', 'target']
        search_fields = ['source__idgloss', 'target__idgloss']

    class Meta:
        ordering = ['source']
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')

    def __str__(self):
        return str(self.source)+' -> ' + str(self.target)


@python_2_unicode_compatible
class MorphologyDefinition(models.Model):
    """Tells something about morphology of a gloss"""
    parent_gloss = models.ForeignKey(
        Gloss, related_name="parent_glosses", on_delete=models.CASCADE)
    # role = models.CharField(max_length=5, choices=(build_choice_list('MorphologyType')))
    role = models.ForeignKey('FieldChoice', to_field='machine_value', db_column='MorphologyType',
                             limit_choices_to={'field': 'MorphologyType'}, blank=True, on_delete=models.CASCADE)
    morpheme = models.ForeignKey(
        Gloss, related_name="morphemes", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Morphology definition')
        verbose_name_plural = _('Morphology definitions')

    def __str__(self):
        return str(self.morpheme.idgloss) + ' is ' + str(self.role) + ' of ' + str(self.parent_gloss.idgloss)


@python_2_unicode_compatible
class Signer(models.Model):
    """The list of signers"""
    #: Signer name.
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Signer')
        verbose_name_plural = _('Signers')

    def __str__(self):
        return self.name


# Register Models for django-tagging to add wrappers around django-tagging API.
models_to_register_for_tagging = (Gloss, GlossRelation,)
for model in models_to_register_for_tagging:
    try:
        tagging_register(model)
    except AlreadyRegistered:
        pass
