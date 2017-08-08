"""Models for the Signbank dictionary database."""
from __future__ import unicode_literals
import json
from collections import OrderedDict

from django.db import models, OperationalError
from django.conf import settings
from django.http import Http404
from django.urls import reverse
from tagging.registry import register
import tagging
import os
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import FieldDoesNotExist
from signbank.video.models import GlossVideo

from signbank.dictionary.choicelists import *


class Dataset(models.Model):
    """A dataset, can be public/private and can be of only one SignLanguage"""
    name = models.CharField(unique=True, blank=False, null=False, max_length=60)
    is_public = models.BooleanField(default=False, help_text="Is this dataset is public or private?")
    signlanguage = models.ForeignKey("SignLanguage")
    translation_languages =  models.ManyToManyField("Language", help_text="These languages are shown as options"
                                                                          "for translation equivalents.")
    description = models.TextField()

    class Meta:
        permissions = (
            ('view_dataset', _('View dataset')),
        )

    def __str__(self):
        return self.name


class GlossTranslations(models.Model):
    """Store a string representation of translation equivalents of certain Language for a Gloss."""
    gloss = models.ForeignKey("Gloss")
    language = models.ForeignKey("Language")
    translations = models.TextField(blank=True)

    class Meta:
        unique_together = (("gloss", "language"),)

    def __str__(self):
        return self.translations


class Translation(models.Model):
    """A translation equivalent of a sign in selected language."""
    gloss = models.ForeignKey("Gloss")
    language = models.ForeignKey("Language")
    keyword = models.ForeignKey("Keyword")
    index = models.IntegerField("Index")

    def __str__(self):
        return self.gloss.idgloss + '-' + self.keyword.text

    class Meta:
        unique_together = (("gloss", "language", "keyword"),)
        ordering = ['gloss', 'index']

    class Admin:
        list_display = ['gloss', 'keyword']
        search_fields = ['gloss__idgloss']


class Keyword(models.Model):
    """A keyword that stores the text for translation(s)"""

    text = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['text']

    class Admin:
        search_fields = ['text']


DEFN_ROLE_CHOICES = (
    # Translators: DEFN_ROLE_CHOICES
    ('note', _('Note')),
    # Translators: DEFN_ROLE_CHOICES
    ('privatenote', _('Private Note')),
    # Translators: DEFN_ROLE_CHOICES
    ('phon', _('Phonology')),
    # Translators: DEFN_ROLE_CHOICES
    ('todo', _('To Do')),
    # Translators: DEFN_ROLE_CHOICES
    ('sugg', _('Suggestion for other gloss')),
)


class Definition(models.Model):
    """An English text associated with a gloss. It's called a note in the web interface"""

    def __str__(self):
        return str(self.gloss) + "/" + str(self.role)

    gloss = models.ForeignKey("Gloss")
    text = models.TextField()
    role = models.CharField("Type", max_length=20, choices=DEFN_ROLE_CHOICES)
    count = models.IntegerField()
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['gloss', 'role', 'count']

    class Admin:
        list_display = ['gloss', 'role', 'count', 'text']
        list_filter = ['role']
        search_fields = ['gloss__idgloss']


class Language(models.Model):
    """A written language, used for translations in written languages."""
    name = models.CharField(max_length=50)
    language_code_2char = models.CharField(unique=False, blank=False, null=False, max_length=2, help_text=_(
        """ISO 639-1 language code (2 characters long) of a written language."""))
    language_code_3char = models.CharField(unique=False, blank=False, null=False, max_length=3, help_text=_(
        """ISO 639-3 language code (3 characters long) of a written language."""))
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SignLanguage(models.Model):
    """A sign language."""
    name = models.CharField(max_length=50)
    language_code_3char = models.CharField(unique=False, blank=False, null=False, max_length=3, help_text=_(
        """ISO 639-3 language code (3 characters long) of a sign language."""))

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Dialect(models.Model):
    """A dialect name - a regional dialect of a given Language"""

    class Meta:
        ordering = ['language', 'name']

    language = models.ForeignKey("SignLanguage")
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return str(self.language.name) + "/" + str(self.name)


class RelationToForeignSign(models.Model):
    """Defines a relationship to another sign in another language (often a loan)"""

    def __str__(self):
        return str(self.gloss) + "/" + str(self.other_lang) + ',' + str(self.other_lang_gloss)

    gloss = models.ForeignKey("Gloss")
    # Translators: RelationToForeignSign field verbose name
    loan = models.BooleanField(_("Loan Sign"), default=False)
    # Translators: RelationToForeignSign field verbose name
    other_lang = models.CharField(_("Related Language"), max_length=20)
    # Translators: RelationToForeignSign field verbose name
    other_lang_gloss = models.CharField(
        _("Gloss in related language"), max_length=50)

    class Meta:
        ordering = ['gloss', 'loan', 'other_lang', 'other_lang_gloss']

    class Admin:
        list_display = ['gloss', 'loan', 'other_lang', 'other_lang_gloss']
        list_filter = ['other_lang']
        search_fields = ['gloss__idgloss']


class FieldChoice(models.Model):
    field = models.CharField(max_length=50)
    english_name = models.CharField(max_length=50)
    machine_value = models.IntegerField(unique=True)

    def __str__(self):
        # return self.field + ': ' + self.english_name + ' (' + str(self.machine_value) + ')'
        return str(self.english_name)

    class Meta:
        ordering = ['field', 'machine_value']


def build_choice_list(field):
    """This function builds a list of choices from FieldChoice."""
    choice_list = []
    # Get choices for a certain field in FieldChoices, append machine_value and english_name
    try:
        for choice in FieldChoice.objects.filter(field=field):
            choice_list.append((str(choice.machine_value), choice.english_name))

        return choice_list
    # Enter this exception if for example the db has no data yet (without this it is impossible to migrate)
    except OperationalError:
        return choice_list


class Gloss(models.Model):
    class Meta:
        unique_together = (("idgloss", "dataset"),)
        # Translators: This is verbose_name_plural, so it has to be plural here
        verbose_name_plural = _("Glosses")
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
            ('can_publish', _('Can publish signs and definitions')),
            # Translators: Gloss permissions
            ('view_advanced_properties', _('Include all properties in sign detail view')),
            # Translators: Gloss permissions
            ('lock_gloss', _('Can lock and unlock Gloss from editing')),
        )
    # *** Fields begin ***

    locked = models.BooleanField(_("Locked"), default=False)

    dataset = models.ForeignKey("Dataset", verbose_name=_("Glosses dataset"),
                                help_text=_("Dataset a gloss is part of"))

    # Gloss in Finnish. This is the unique identifying name of a Gloss.
    # Translators: Gloss field: idgloss, verbose name
    idgloss = models.CharField(_("Gloss"), max_length=60,
                               # Translators: Help text for Gloss field: idgloss
                               help_text=_("""This is the unique identifying name of a Gloss."""))

    # Gloss in English. This is the English name of a Gloss.
    # Translators: Gloss field: idgloss_en (english), verbose name
    idgloss_en = models.CharField(_("Gloss in English"), blank=True, max_length=60,
                                                 # Translators: Help text for Gloss field: idgloss_en (english)
                                                 help_text=_("""This is the English name for the Gloss"""))

    # Translators: Gloss models field: annotation_comments, verbose name
    annotation_comments = models.CharField(_("Comments"), max_length=200, blank=True)

    # Translators: Gloss models field: url
    url_field = models.URLField(_("URL"), max_length=200, blank=True, unique=False)

    ########

    # One or more regional dialects that this gloss is used in
    dialect = models.ManyToManyField(Dialect, blank=True)

    # Fields representing creation time, updated_at time, creator and updater
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_by_user')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='updated_by_user')

    # ### Phonology fields ###
    # Translators: Gloss models field: handedness, verbose name
    # handedness = models.CharField(_("Handedness"), blank=True, null=True, choices=build_choice_list("handedness"),
    #                               max_length=5)  # handednessChoices <- use this if you want static
    handedness = models.ForeignKey('FieldChoice', verbose_name=_("Handedness"), to_field='machine_value',
                                   db_column='handedness', limit_choices_to={'field': 'handedness'},
                                   related_name="handedness", blank=True, null=True)
    # Translators: Gloss models field: strong_handshape, verbose name
    # strong_handshape = models.CharField(_("Strong Hand"), blank=True, null=True, choices=build_choice_list("handshape"),
    #                                     max_length=5)
    strong_handshape = models.ForeignKey('FieldChoice', verbose_name=_("Strong Hand"), to_field='machine_value',
                                         db_column='strong_handshape', limit_choices_to={'field': 'strong_handshape'},
                                         related_name="strong_handshape", blank=True, null=True)

    # Translators: Gloss models field: weak_handshape, verbose name
    # weak_handshape = models.CharField(_("Weak Hand"), null=True, choices=build_choice_list("handshape"), blank=True,
    #                                  max_length=5)
    weak_handshape = models.ForeignKey('FieldChoice', verbose_name=_("Weak Hand"), to_field='machine_value',
                                       db_column='weak_handshape', limit_choices_to={'field': 'weak_handshape'},
                                       related_name="weak_handshape", blank=True, null=True)

    # Translators: Gloss models field: location, verbose name
    # location = models.CharField(
    #     _("Location"), choices=build_choice_list("location"), null=True, blank=True, max_length=20)
    location = models.ForeignKey('FieldChoice', verbose_name=_("Location"), to_field='machine_value',
                                 db_column='location', limit_choices_to={'field': 'location'}, related_name="location",
                                 blank=True, null=True)

    # Translators: Gloss models field: relation_between_articulators, verbose name
    # relation_between_articulators = models.CharField(
    #    _("Relation between Articulators"), choices=build_choice_list("relation_between_articulators"),
    #    null=True, blank=True, max_length=5)
    relation_between_articulators = models.ForeignKey('FieldChoice', verbose_name=_("Relation Between Articulators"),
                                                      to_field='machine_value',
                                                      db_column='relation_between_articulators',
                                                      limit_choices_to={'field': 'relation_between_articulators'},
                                                      related_name="relation_between_articulators", blank=True,
                                                      null=True)

    # Translators: Gloss models field: absolute_orientation_palm, verbose name
    # absolute_orientation_palm = models.CharField(_("Absolute Orientation: Palm"),
    #                                             choices=build_choice_list("relation_between_articulators"), null=True,
    #                                             blank=True, max_length=5)
    absolute_orientation_palm = models.ForeignKey('FieldChoice', verbose_name=_("Absolute Orientation: Palm"),
                                                  to_field='machine_value', db_column='absolute_orientation_palm',
                                                  limit_choices_to={'field': 'absolute_orientation_palm'},
                                                  related_name="absolute_orientation_palm", blank=True, null=True)
    # Translators: Gloss models field: absolute_orientation_fingers, verbose name
    # absolute_orientation_fingers = models.CharField(_("Absolute Orientation: Fingers"),
    #                                                choices=build_choice_list("absolute_orientation_fingers"),
    #                                                null=True,
    #                                                blank=True, max_length=5)
    absolute_orientation_fingers = models.ForeignKey('FieldChoice', verbose_name=_("Absolute Orientation: Fingers"),
                                                     to_field='machine_value', db_column='absolute_orientation_fingers',
                                                     limit_choices_to={'field': 'absolute_orientation_fingers'},
                                                     related_name="absolute_orientation_fingers", blank=True, null=True)

    # Translators: Gloss models field: relative_orientation_movement, verbose name
    # relative_orientation_movement = models.CharField(_("Relative Orientation: Movement"),
    #                                                 choices=build_choice_list("relative_orientation_movement"),
    #                                                 null=True,
    #                                                 blank=True, max_length=5)
    relative_orientation_movement = models.ForeignKey('FieldChoice', verbose_name=_("Relative Orientation: Movement"),
                                                      to_field='machine_value',
                                                      db_column='relative_orientation_movement',
                                                      limit_choices_to={'field': 'relative_orientation_movement'},
                                                      related_name="relative_orientation_movement", blank=True,
                                                      null=True)
    # Translators: Gloss models field: relative_orientation_location, verbose name
    # relative_orientation_location = models.CharField(_("Relative Orientation: Location"),
    #                                                 choices=build_choice_list("relative_orientation_location"),
    #                                                 null=True,
    #                                                 blank=True, max_length=5)
    relative_orientation_location = models.ForeignKey('FieldChoice', verbose_name=_("Relative Orientation: Location"),
                                                      to_field='machine_value',
                                                      db_column='relative_orientation_location',
                                                      limit_choices_to={'field': 'relative_orientation_location'},
                                                      related_name="relative_orientation_location", blank=True,
                                                      null=True)
    # Translators: Gloss models field: orientation_change, verbose name
    # orientation_change = models.CharField(_("Orientation Change"), choices=build_choice_list("orientation_change"),
    #                                      null=True, blank=True,
    #                                      max_length=5)
    orientation_change = models.ForeignKey('FieldChoice', verbose_name=_("Orientation Change"),
                                           to_field='machine_value', db_column='orientation_change',
                                           limit_choices_to={'field': 'orientation_change'},
                                           related_name="orientation_change", blank=True, null=True)

    # Translators: Gloss models field: handshape_change, verbose name
    # handshape_change = models.CharField(_("Handshape Change"), choices=build_choice_list("handshape_change"), null=True,
    #                                    blank=True,
    #                                    max_length=5)
    handshape_change = models.ForeignKey('FieldChoice', verbose_name=_("Handshape Change"), to_field='machine_value',
                                         db_column='handshape_change', limit_choices_to={'field': 'handshape_change'},
                                         related_name="handshape_change", blank=True, null=True)

    # Translators: Gloss models field: repeated_movement, verbose name
    repeated_movement = models.NullBooleanField(_("Repeated Movement"), null=True, default=False)
    # Translators: Gloss models field: alternating_movement, verbose name
    alternating_movement = models.NullBooleanField(_("Alternating Movement"), null=True, default=False)

    # Translators: Gloss models field: movement_shape, verbose name
    # movement_shape = models.CharField(_("Movement Shape"), choices=build_choice_list("movement_shape"), null=True,
    #                                  blank=True,
    #                                  max_length=5)
    movement_shape = models.ForeignKey('FieldChoice', verbose_name=_("Movement Shape"), to_field='machine_value',
                                       db_column='movement_shape', limit_choices_to={'field': 'movement_shape'},
                                       related_name="movement_shape", blank=True, null=True)
    # Translators: Gloss models field: movement_direction, verbose name
    # movement_direction = models.CharField(_("Movement Direction"), choices=build_choice_list("movement_direction"),
    #                                      null=True, blank=True,
    #                                      max_length=5)
    movement_direction = models.ForeignKey('FieldChoice', verbose_name=_("Movement Direction"),
                                           to_field='machine_value', db_column='movement_direction',
                                           limit_choices_to={'field': 'movement_direction'},
                                           related_name="movement_direction", blank=True, null=True)
    # Translators: Gloss models field: movement_manner, verbose name
    # movement_manner = models.CharField(_("Movement Manner"), choices=build_choice_list("movement_manner"), null=True,
    #                                   blank=True,
    #                                   max_length=5)
    movement_manner = models.ForeignKey('FieldChoice', verbose_name=_("Movement Manner"), to_field='machine_value',
                                        db_column='movement_manner', limit_choices_to={'field': 'movement_manner'},
                                        related_name="movement_manner", blank=True, null=True)
    # Translators: Gloss models field: contact_type, verbose name
    # contact_type = models.CharField(_("Contact Type"), choices=build_choice_list("contact_type"), null=True, blank=True,
    #                                max_length=5)
    contact_type = models.ForeignKey('FieldChoice', verbose_name=_("Contact Type"), to_field='machine_value',
                                     db_column='contact_type', limit_choices_to={'field': 'contact_type'},
                                     related_name="contact_type", blank=True, null=True)

    # Translators: Gloss models field: phonology_other verbose name
    phonology_other = models.TextField(_("Phonology Other"), null=True, blank=True)

    # Translators: Gloss models field: mouth_gesture, verbose name
    mouth_gesture = models.CharField(_("Mouth Gesture"), max_length=50, blank=True)
    # Translators: Gloss models field: mouthing, verbose name
    mouthing = models.CharField(_("Mouthing"), max_length=50, blank=True)
    # Translators: Gloss models field: phonetic_variation, verbose name
    phonetic_variation = models.CharField(_("Phonetic Variation"), max_length=50, blank=True, )

    # ### Semantic fields
    # Translators: Gloss models field: iconic_image, verbose name
    iconic_image = models.CharField(_("Iconic Image"), max_length=50, blank=True)
    # Translators: Gloss models field: named_entity, verbose name
    # named_entity = models.CharField(_("Named Entity"), choices=build_choice_list("named_entity"), null=True, blank=True,
    #                                max_length=5)
    named_entity = models.ForeignKey('FieldChoice', verbose_name=_("Named Entity"), to_field='machine_value',
                                     db_column='named_entity', limit_choices_to={'field': 'named_entity'},
                                     related_name="named_entity", blank=True, null=True)
    # Translators: Gloss models field: semantic_field, verbose name
    # semantic_field = models.CharField(_("Semantic Field"), choices=build_choice_list("semantic_field"), null=True,
    #                                  blank=True,
    #                                  max_length=5)
    semantic_field = models.ForeignKey('FieldChoice', verbose_name=_("Semantic Field"), to_field='machine_value',
                                       db_column='semantic_field', limit_choices_to={'field': 'semantic_field'},
                                       related_name="semantic_field", blank=True, null=True)

    # ### Frequency fields
    # Translators: Gloss models field_ number_of_occurences, verbose name
    number_of_occurences = models.IntegerField(
        _("Number of Occurrences"), null=True, blank=True,
        # Translators: Help text for Gloss models field: number_of_occurences
        help_text=_("Number of occurences in annotation materials"))

    # ### Publication status
    # Translators: Gloss models field: in_web_dictionary, verbose name
    in_web_dictionary = models.NullBooleanField(_("In the Web dictionary"), default=False)
    # Translators: Gloss models field: is_proposed_new_sign, verbose name
    is_proposed_new_sign = models.NullBooleanField(
        _("Is this a proposed new sign?"), null=True, default=False)

    def __str__(self):
        return "%s" % (str(self.idgloss))

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
        # Dataset is available to Language due to m2m field on Dataset for Language.
        return Language.objects.filter(dataset=self.dataset)

    def get_translations_for_translation_languages(self):
        """Returns a zipped list of translation languages and translations."""
        translation_list = []
        translation_languages = self.get_translation_languages()
        for language in translation_languages:
            try:
                # Get translations from GlossTranslation object, if it exists for gloss+language.
                translation_list.append(GlossTranslations.objects.get(gloss=self, language=language))
            except GlossTranslations.DoesNotExist:
                # If it doesn't exist, try to get translations from Translation objects.
                translations = Translation.objects.filter(gloss=self, language=language)
                kwd_str = ""
                first = True
                for trans in translations:
                    if first:
                        kwd_str += str(trans.keyword)
                        first = False
                    else:
                        kwd_str += ", " + str(trans.keyword)
                translation_list.append(kwd_str)

        return list(zip(translation_languages, translation_list))

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Gloss._meta.fields]

    def options_to_json(self, options):
        """Convert an options list to a json dict"""

        result = []
        for k, v in options:
            result.append('"%s":"%s"' % (k, v))
        return "{" + ",".join(result) + "}"

    def handshape_choices_json(self):
        """Return JSON for the handshape choice list"""

        return self.options_to_json(handshape_choices)

    def location_choices_json(self):
        """Return JSON for the location choice list"""

        return self.options_to_json(location_choices)

    def palm_orientation_choices_json(self):
        """Return JSON for the palm orientation choice list"""

        return self.options_to_json(palm_orientation_choices)

    def relative_orientation_choices_json(self):
        """Return JSON for the relative orientation choice list"""

        return self.options_to_json(relative_orientation_choices)

    def secondary_location_choices_json(self):
        """Return JSON for the secondary location (BSL) choice list"""

        return self.options_to_json(BSLsecondLocationChoices)

    def definition_role_choices_json(self):
        """Return JSON for the definition role choice list"""

        return self.options_to_json(DEFN_ROLE_CHOICES)

    def relation_role_choices_json(self):
        """Return JSON for the relation role choice list"""

        return self.options_to_json(RELATION_ROLE_CHOICES)

    def language_choices(self):
        """Return JSON for langauge choices"""

        d = dict()
        for l in Language.objects.all():
            d[l.name] = l.name

        return json.dumps(d)

    @staticmethod
    def dialect_choices():
        """Return JSON for dialect choices"""

        d = dict()
        for l in Dialect.objects.all():
            d[l.name] = l.name

        return json.dumps(d)

    @staticmethod
    def get_choice_lists():
        """Return JSON for the location choice list"""

        choice_lists = {}

        # Start with your own choice lists
        for fieldname in ['handedness', 'location', 'strong_handshape', 'weak_handshape',
                          'relation_between_articulators', 'absolute_orientation_palm', 'absolute_orientation_fingers',
                          'relative_orientation_movement', 'relative_orientation_location', 'handshape_change',
                          'repeated_movement', 'alternating_movement', 'movement_shape', 'movement_direction',
                          'movement_manner', 'contact_type', 'named_entity', 'orientation_change', 'semantic_field']:
            # Get the list of choices for this field
            # li = self._meta.get_field(fieldname).choices
            li = build_choice_list(fieldname)

            # Sort the list
            sorted_li = sorted(li, key=lambda x: x[1])

            # Put it in another format
            reformatted_li = [('_' + str(value), text)
                              for value, text in sorted_li]
            choice_lists[fieldname] = OrderedDict(reformatted_li)

        # Choice lists for other models
        # choice_lists['morphology_role'] = [human_value for machine_value, human_value in
        #                                   build_choice_list('MorphologyType')]
        choice_lists['morphology_role'] = build_choice_list('MorphologyType')
        reformatted_morph_role = [('_' + str(value), text)
                                  for value, text in choice_lists['morphology_role']]
        choice_lists['morphology_role'] = OrderedDict(reformatted_morph_role)
        # morphology_role
        return json.dumps(choice_lists)

# Register Gloss for tags
try:
    register(Gloss)
except tagging.registry.AlreadyRegistered:
    pass


class GlossURL(models.Model):
    """URL's for gloss"""
    gloss = models.ForeignKey('Gloss')
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.gloss.idgloss + " - " + self.url


class GlossRelation(models.Model):
    """Relation between two glosses"""

    source = models.ForeignKey(Gloss, related_name="glossrelation_source")
    target = models.ForeignKey(Gloss, related_name="glossrelation_target")

    class Admin:
        list_display = ['source', 'role', 'target']
        search_fields = ['source__idgloss', 'target__idgloss']

    class Meta:
        ordering = ['source']

    def __str__(self):
        return str(self.target)


RELATION_ROLE_CHOICES = (
    # Translators: RELATION_ROLE_CHOICES
    ('homonym', _('Homonym')),
    # Translators: RELATION_ROLE_CHOICES
    ('synonym', _('Synonym')),
    # Translators: RELATION_ROLE_CHOICES
    ('variant', _('Variant')),
    # Translators: RELATION_ROLE_CHOICES
    ('antonym', _('Antonym')),
    # Translators: RELATION_ROLE_CHOICES
    ('hyponym', _('Hyponym')),
    # Translators: RELATION_ROLE_CHOICES
    ('hypernym', _('Hypernym')),
    # Translators: RELATION_ROLE_CHOICES
    ('seealso', _('See Also')),
)


class Relation(models.Model):
    """A relation between two glosses"""

    source = models.ForeignKey(Gloss, related_name="relation_sources")
    target = models.ForeignKey(Gloss, related_name="relation_targets")
    # role = models.CharField(max_length=20, choices=build_choice_list('MorphologyType'))
    role = models.ForeignKey('FieldChoice', to_field='machine_value', db_column='MorphologyType',
                             limit_choices_to={'field': 'MorphologyType'}, blank=True)
    # antonym, synonym, cf (what's this? - see also), var[b-f]
    # (what's this - variant (XXXa is the stem, XXXb is a variant)

    class Admin:
        list_display = ['source', 'role', 'target']
        search_fields = ['source__idgloss', 'target__idgloss']

    class Meta:
        ordering = ['source']


class MorphologyDefinition(models.Model):
    """Tells something about morphology of a gloss"""

    parent_gloss = models.ForeignKey(Gloss, related_name="parent_glosses")
    # role = models.CharField(max_length=5, choices=(build_choice_list('MorphologyType')))
    role = models.ForeignKey('FieldChoice', to_field='machine_value', db_column='MorphologyType',
                             limit_choices_to={'field': 'MorphologyType'}, blank=True)
    morpheme = models.ForeignKey(Gloss, related_name="morphemes")

    def __str__(self):
        # return str(self.morpheme.idgloss) + ' is ' + str(self.get_role_display()) + ' of ' + str(
        #    self.parent_gloss.idgloss)
        return str(
            self.morpheme.idgloss + ' is ' + str(self.role) + ' of ' + str(self.parent_gloss.idgloss))
