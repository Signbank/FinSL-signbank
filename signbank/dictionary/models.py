"""Models for the NGT database.

These are refactored from the original database to 
normalise the data and hopefully make it more
manageable.  

"""

from django.db.models import Q
from django.db import models, OperationalError
from django.conf import settings
from django.http import Http404
import tagging

import sys
import os
import json
from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _

# from signbank.video.models import GlossVideo

# from models_legacy import Sign


class Translation(models.Model):
    """A Dutch translation of NGT signs"""

    gloss = models.ForeignKey("Gloss")
    translation = models.ForeignKey("Keyword")
    index = models.IntegerField("Index")

    def __unicode__(self):
        return self.gloss.idgloss + '-' + self.translation.text

    def get_absolute_url(self):
        """Return a URL for a view of this translation."""

        alltrans = self.translation.translation_set.all()
        idx = 0
        for tr in alltrans:
            if tr == self:
                return "/dictionary/words/" + str(self.translation) + "-" + str(idx + 1) + ".html"

            idx += 1
        return "/dictionary/"

    class Meta:
        ordering = ['gloss', 'index']

    class Admin:
        list_display = ['gloss', 'translation']
        search_fields = ['gloss__idgloss']


class Keyword(models.Model):
    """A Dutch keyword that is a possible translation equivalent of a sign"""

    def __unicode__(self):
        return self.text

    text = models.CharField(max_length=100, unique=True)

    def in_web_dictionary(self):
        """Return True if some gloss associated with this
        keyword is in the web version of the dictionary"""

        return len(self.translation_set.filter(gloss__in_web_dictionary__exact=True)) != 0

    class Meta:
        ordering = ['text']

    class Admin:
        search_fields = ['text']

    def match_request(self, request, n):
        """Find the translation matching a keyword request given an index 'n'
        response depends on login status
        Returns a tuple (translation, count) where count is the total number
        of matches."""

        if request.user.has_perm('dictionary.search_gloss'):
            alltrans = self.translation_set.all()
        else:
            alltrans = self.translation_set.filter(gloss__inWeb__exact=True)

        # remove crude signs for non-authenticated users if ANON_SAFE_SEARCH is
        # on
        try:
            crudetag = tagging.models.Tag.objects.get(name='lexis:crude')
        except:
            crudetag = None

        safe = (not request.user.is_authenticated()
                ) and settings.ANON_SAFE_SEARCH
        if safe and crudetag:
            alltrans = [
                tr for tr in alltrans if not crudetag in tagging.models.Tag.objects.get_for_object(tr.gloss)]

        # if there are no translations, generate a 404
        if len(alltrans) == 0:
            raise Http404

        # take the nth translation if n is in range
        # otherwise take the last
        if n - 1 < len(alltrans):
            trans = alltrans[n - 1]
        else:
            trans = alltrans[len(alltrans) - 1]

        return (trans, len(alltrans))


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

    def __unicode__(self):
        return unicode(self.gloss) + "/" + unicode(self.role)

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
    """A sign language name"""

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=20)
    description = models.TextField()

    def __unicode__(self):
        return unicode(self.name)


class Dialect(models.Model):
    """A dialect name - a regional dialect of a given Language"""

    class Meta:
        ordering = ['language', 'name']

    language = models.ForeignKey(Language)
    name = models.CharField(max_length=20)
    description = models.TextField()

    def __unicode__(self):
        return unicode(self.language.name) + "/" + unicode(self.name)


class RelationToForeignSign(models.Model):
    """Defines a relationship to another sign in another language (often a loan)"""

    def __unicode__(self):
        return unicode(self.gloss) + "/" + unicode(self.other_lang) + ',' + unicode(self.other_lang_gloss)

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

# TODO: Remove all these choice lists
handednessChoices = (('0', 'No Value Set'),
                     ('1', 'N/A'),
                     ('2', '1'),
                     ('3', '2'),
                     ('4', '2a'),
                     ('5', '2s'),
                     ('6', 'X'))

handshapeChoices = (('0', 'No Value Set'),
                    ('1', 'N/A'),
                    ('2', 'J + beak2'),
                    ('3', '5'),
                    ('4', 'Money'),
                    ('5', 'V'),
                    ('6', 'B'),
                    ('7', 'Y'),
                    ('8', 'S'),
                    ('9', 'L'),
                    ('10', 'Baby-c'),
                    ('11', 'B-relaxed'),
                    ('12', 'C-spread'),
                    ('13', 'B-curved'),
                    ('14', 'N'),
                    ('15', '1'),
                    ('16', 'W'),
                    ('17', 'Beak2'),
                    ('18', 'Q'),
                    ('19', '5r'),
                    ('20', 'V-curved'),
                    ('21', '1-curved'),
                    ('22', 'Beak'),
                    ('23', 'Beak2-spread'),
                    ('24', 'A'),
                    ('25', 'I'),
                    ('26', 'B-bent'),
                    ('27', 'C'),
                    ('28', 'T'),
                    ('29', 'Baby-beak'),
                    ('30', '5m'),
                    ('31', 'Shower'),
                    ('32', 'O'),
                    ('33', 'Flexed arm'),
                    ('34', 'D'),
                    ('35', '4'),
                    ('36', 'M + v'),
                    ('37', '3'),
                    ('38', 'Baby-o'),
                    ('39', 'F'),
                    ('40', 'M'),
                    ('41', 'Flower'),
                    ('42', 'K'),
                    ('43', '5mx'),
                    ('44', 'B + s'),
                    ('45', 'Asl-t'),
                    ('46', 'O2'),
                    ('47', 'R'),
                    ('48', '9'),
                    ('49', '5rx'),
                    ('50', 'Beak, pinkie extended'),
                    ('51', 'S + w'),
                    ('52', 'L2'),
                    ('53', 'L-curved'),
                    ('54', 'W-curved'),
                    ('55', 'Q5'),
                    ('56', 'E'),
                    ('57', 'T + l'),
                    ('58', 'N + e'),
                    ('59', 'Horns'),
                    ('60', 'P'),
                    ('61', 'C-spread, index extended'),
                    ('62', 'Baby-c'),
                    ('63', 'Money-open'),
                    ('64', 'Beak, index extended'),
                    ('65', '5px'),
                    ('66', 'Y mrp-bent'),
                    ('67', 'Mrp-bent'),
                    ('68', 'Mrp-curved'),
                    ('69', 'O3'),
                    ('70', 'T + v'),
                    ('71', 'V + o'),
                    ('72', 'C, extended index'),
                    ('73', '5 + v'),
                    ('74', 'A-curved'),
                    ('75', 'C-spread-2'),
                    ('76', 'J + l'),
                    ('77', 'J + n'),
                    ('78', 'L + mrp bent'),
                    ('79', 'O + k'),
                    ('80', 'Middle finger'),
                    ('81', '1 + m'),
                    ('82', 'S + i'))

locationChoices = (('0', 'No Value Set'),
                   ('1', 'N/A'),
                   ('2', 'Neutral space > head'),
                   ('3', 'Neutral space'),
                   ('4', 'Shoulder'),
                   ('5', 'Weak hand'),
                   ('6', 'Weak hand > arm'),
                   ('7', 'Forehead'),
                   ('8', 'Chest'),
                   ('9', 'Neck'),
                   ('10', 'Head'),
                   ('11', 'Weak hand: back'),
                   ('12', 'Chin'),
                   ('13', 'Ring finger'),
                   ('14', 'Forehead, belly'),
                   ('15', 'Eye'),
                   ('16', 'Cheekbone'),
                   ('17', 'Face'),
                   ('18', 'Ear'),
                   ('19', 'Mouth'),
                   ('20', 'Low in neutral space'),
                   ('21', 'Arm'),
                   ('22', 'Nose'),
                   ('23', 'Cheek'),
                   ('24', 'Heup'),
                   ('25', 'Body'),
                   ('26', 'Belly'),
                   ('27', 'Tongue'),
                   ('28', 'Chin > neutral space'),
                   ('29', 'Locative'),
                   ('30', 'Head ipsi'),
                   ('31', 'Forehead > chin'),
                   ('32', 'Head > shoulder'),
                   ('33', 'Chin > weak hand'),
                   ('34', 'Forehead > chest'),
                   ('35', 'Borst contra'),
                   ('36', 'Weak hand: palm'),
                   ('37', 'Back of head'),
                   ('38', 'Above head'),
                   ('39', 'Next to trunk'),
                   ('40', 'Under chin'),
                   ('41', 'Head > weak hand'),
                   ('42', 'Borst ipsi'),
                   ('43', 'Temple'),
                   ('44', 'Upper leg'),
                   ('45', 'Leg'),
                   ('46', 'Mouth ipsi'),
                   ('47', 'High in neutral space'),
                   ('48', 'Mouth > chest'),
                   ('49', 'Chin ipsi'),
                   ('50', 'Wrist'),
                   ('51', 'Lip'),
                   ('52', 'Neck > chest'),
                   ('53', 'Cheek + chin'),
                   ('54', 'Upper arm'),
                   ('55', 'Shoulder contra'),
                   ('56', 'Forehead > weak hand'),
                   ('57', 'Neck ipsi'),
                   ('58', 'Mouth > weak hand'),
                   ('59', 'Weak hand: thumb side'),
                   ('60', 'Between thumb and index finger'),
                   ('61', 'Neutral space: high'),
                   ('62', 'Chin contra'),
                   ('63', 'Upper lip'),
                   ('64', 'Forehead contra'),
                   ('65', 'Side of upper body'),
                   ('66', 'Weak hand: tips'),
                   ('67', 'Mouth + chin'),
                   ('68', 'Side of head'),
                   ('69', 'Head > neutral space'),
                   ('70', 'Chin > chest'),
                   ('71', 'Face + head'),
                   ('72', 'Cheek contra'),
                   ('73', 'Belly ipsi'),
                   ('74', 'Chest contra'),
                   ('75', 'Neck contra'),
                   ('76', 'Back of the head'),
                   ('77', 'Elbow'),
                   ('78', 'Temple > chest'),
                   ('79', 'Thumb'),
                   ('80', 'Middle finger'),
                   ('81', 'Pinkie'),
                   ('82', 'Index finger'),
                   ('83', 'Back'),
                   ('84', 'Ear > cheek'),
                   ('85', 'Knee'),
                   ('86', 'Shoulder contra > shoulder ipsi'),
                   ('87', 'Mouth + cheek'))

# these are values for prim2ndloc fin2ndloc introduced for BSL, the names
# might change
BSLsecondLocationChoices = (
    ('notset', 'No Value Set'),
    ('0', 'N/A'),
    ('back', 'Back'),
    ('palm', 'Palm'),
    ('radial', 'Radial'),
    ('ulnar', 'Ulnar'),
    ('fingertip(s)', 'Fingertips'),
    ('root', 'Root')
)

palmOrientationChoices = (
    ('notset', 'No Value Set'),
    ('prone', 'Prone'),
    ('neutral', 'Neutral'),
    ('supine', 'Supine'),
    ('0', 'N/A'),
)

relOrientationChoices = (
    ('notset', 'No Value Set'),
    ('palm', 'Palm'),
    ('back', 'Back'),
    ('root', 'Root'),
    ('radial', 'Radial'),
    ('ulnar', 'Ulnar'),
    ('fingertip(s)', 'Fingertips'),
    ('0', 'N/A'),
)

relatArticChoices = (
    ("0", 'No Value Set'),
    ("1", 'N/A'),
    ("2", 'One hand behind the other'),
    ("3", 'One hand above the other'),
    ("4", 'Hands move around each other'),
    ("5", 'Strong hand passes through weak hand'),
    ("6", 'One hand after the other'),
    ("7", 'One hand on top of the other'),
    ("8", 'Around the weak hand'),
    ("9", 'Strong hand moves through weak hand'),
    ("10", 'Fingers interwoven'),
    ("11", 'Weak hand within strong hand'),
    ("12", 'Hands rotate around each other'),
    ("13", 'Fingertips touching'),
    ("14", 'Passing under the weak hand'),
    ("15", 'Passing above the wrist'),
    ("16", 'Passing over the weak hand'),
    ("17", 'Strong hand behind weak hand'),
    ("18", 'Strong hand around weak hand'),
    ("19", 'Hands interlocked between thumb and index'),
    ("20", 'Hands cross'),
    ("21", 'Hands overlap'),
    ("22", 'Hand appears behind weak hand'),
    ("23", 'Strong hand under weak hand'),
    ("24", 'One hand above or beside the other'),
    ("25", 'Hands start crossed'),
    ("26", 'Hands move in tandem'),
    ("27", 'Interlocked'),
    ("28", 'One hand a bit higher'),
    ("29", 'Strong hand hangs across weak hand'),
    ("30", 'Strong hand moves over tips of weak hand'),
    ("31", 'Fingers interlocked'),
    ("32", 'Weak hand around thumb'),
    ("33", 'Movement mirrored'),
    ("34", 'Hands rotate around each other, then contacting movement'),
    ("35", 'Thumbs rotate about each other'),
    ("36", 'Hands rotate in the same direction'),
    ("37", 'Crossed'),
    ("38", 'Below the weak hand'),
)

absOriPalmChoices = (
    ('0', 'No Value Set'),
    ('1', 'N/A'),
    ('2', 'Downwards'),
    ('3', 'Towards each other'),
    ('4', 'Backwards'),
    ('5', 'Upwards'),
    ('6', 'Inwards'),
    ('7', 'Forwards'),
    ('8', 'Backwards > forwards'),
    ('9', 'Inwards, forwards'),
    ('10', 'Forwards, sidewards'),
    ('11', 'Downwards, sidewards'),
    ('12', 'Variable'),
    ('13', 'Outwards'),
    ('14', 'Backs towards each other'),
    ('15', 'Inwards > backwards'),
    ('16', 'Sidewards'),
    ('17', 'Forwards, downwards'),
)

absOriFingChoices = (
    ('0', 'No Value Set'),
    ('1', 'N/A'),
    ('2', 'Inwards'),
    ('3', 'Downwards'),
    ('4', 'Upwards'),
    ('5', 'Upwards, forwards'),
    ('6', 'Forwards'),
    ('7', 'Backwards'),
    ('8', 'Towards location'),
    ('9', 'Inwards, upwards'),
    ('10', 'Back/palm'),
    ('11', 'Towards each other'),
    ('12', 'Neutral'),
    ('13', 'Forwards > inwards'),
    ('14', 'Towards weak hand'),
)

relOriMovChoices = (
    ('0', 'No Value Set'),
    ('1', 'N/A'),
    ('2', 'Pinkie'),
    ('3', 'Palm'),
    ('4', 'Tips'),
    ('5', 'Thumb'),
    ('6', 'Basis'),
    ('7', 'Back'),
    ('8', 'Thumb/pinkie'),
    ('9', 'Variable'),
    ('10', 'Basis + palm'),
    ('11', 'Basis + basis'),
    ('12', 'Pinkie + back'),
    ('13', 'Palm > basis'),
    ('14', 'Palm > back'),
    ('15', 'Back > palm'),
    ('16', 'Basis, pinkie'),
    ('17', 'Pinkie > palm'),
    ('18', 'Basis > pinkie'),
    ('19', 'Pinkie > palm > thumb'),
    ('20', 'Back > basis'),
    ('21', 'Thumb > pinkie'),
)

relOriLocChoices = (
    ('0', 'No Value Set'),
    ('1', 'N/A'),
    ('2', 'Pinkie/thumb'),
)

handChChoices = (
    ("0", 'No Value Set'),
    ("1", 'N/A'),
    ("2", '+ closing'),
    ("3", 'Closing, opening'),
    ("4", 'Closing a little'),
    ("5", 'Opening'),
    ("6", 'Closing'),
    ("7", 'Bending'),
    ("8", 'Curving'),
    ("9", 'Wiggle'),
    ("10", 'Unspreading'),
    ("11", 'Extension'),
    ("12", '>5'),
    ("13", 'Partly closing'),
    ("14", 'Closing one by one'),
    ("15", '>s'),
    ("16", '>b'),
    ("17", '>a'),
    ("18", '>1'),
    ("19", 'Wiggle, closing'),
    ("20", 'Thumb rubs finger'),
    ("21", 'Spreading'),
    ("22", '>i'),
    ("23", '>l'),
    ("24", '>5m'),
    ("25", 'Thumb rubs fingers'),
    ("26", 'Thumb curving'),
    ("27", 'Thumbfold'),
    ("28", 'Finger rubs thumb'),
    ("29", '>o'),
    ("30", '>t'),
    ("31", 'Extension one by one'),
)

movShapeChoices = (
    ("0", 'No Value Set'),
    ("1", 'N/A'),
    ("2", 'Circle sagittal > straight'),
    ("3", 'Rotation > straight'),
    ("4", 'Arc'),
    ("5", 'Rotation'),
    ("6", 'Straight'),
    ("7", 'Flexion'),
    ("8", 'Circle sagittal'),
    ("9", 'Arc horizontal'),
    ("10", 'Arc up'),
    ("11", 'Question mark'),
    ("12", 'Zigzag'),
    ("13", 'Arc outside'),
    ("14", 'Circle horizontal'),
    ("15", 'Extension'),
    ("16", 'Abduction'),
    ("17", 'Straight > abduction'),
    ("18", 'Z-shape'),
    ("19", 'Straight + straight'),
    ("20", 'Arc > straight'),
    ("21", 'Parallel arc > straight'),
    ("22", 'Zigzag > straight'),
    ("23", 'Arc down'),
    ("24", 'Arc + rotation'),
    ("25", 'Arc + flexion'),
    ("26", 'Circle parallel'),
    ("27", 'Arc front'),
    ("28", 'Circle horizontal small'),
    ("29", 'Arc back'),
    ("30", 'Waving'),
    ("31", 'Straight, rotation'),
    ("32", 'Circle parallel + straight'),
    ("33", 'Down'),
    ("34", 'Thumb rotation'),
    ("35", 'Circle sagittal small'),
    ("36", 'Heart-shape'),
    ("37", 'Circle'),
    ("38", 'Cross'),
    ("39", 'Supination'),
    ("40", 'Pronation'),
    ("41", 'M-shape'),
    ("42", 'Circle sagittal big'),
    ("43", 'Circle parallel small'),
)

movDirChoices = (
    ("0", 'No Value Set'),
    ("1", 'N/A'),
    ("2", '+ forward'),
    ("3", '> downwards'),
    ("4", '> forwards'),
    ("5", 'Backwards'),
    ("6", 'Backwards > downwards'),
    ("7", 'Directional'),
    ("8", 'Downwards'),
    ("9", 'Downwards + inwards'),
    ("10", 'Downwards + outwards'),
    ("11", 'Downwards > inwards'),
    ("12", 'Downwards > outwards'),
    ("13", 'Downwards > outwards, downwards'),
    ("14", 'Downwards, inwards'),
    ("15", 'Forward'),
    ("16", 'Forwards'),
    ("17", 'Forwards > downwards'),
    ("18", 'Forwards > inwards'),
    ("19", 'Forwards > sidewards > forwards'),
    ("20", 'Forwards-backwards'),
    ("21", 'Forwards, downwards'),
    ("22", 'Forwards, inwards'),
    ("23", 'Forwards, outwards'),
    ("24", 'Forwards, upwards'),
    ("25", 'Hands approach vertically'),
    ("26", 'Inwards'),
    ("27", 'Inwards > forwards'),
    ("28", 'Inwards, downwards'),
    ("29", 'Inwards, forwards'),
    ("30", 'Inwards, upwards'),
    ("31", 'No movement'),
    ("32", 'Upwards'),
    ("33", 'Upwards > downwards'),
    ("34", 'Up and down'),
    ("35", 'Upwards, inwards'),
    ("36", 'Upwards, outwards'),
    ("37", 'Upwards, forwards'),
    ("38", 'Outwards'),
    ("39", 'Outwards > downwards'),
    ("40", 'Outwards > downwards > inwards'),
    ("41", 'Outwards > upwards'),
    ("42", 'Outwards, downwards > downwards'),
    ("43", 'Outwards, forwards'),
    ("44", 'Outwards, upwards'),
    ("45", 'Rotation'),
    ("46", 'To and fro'),
    ("47", 'To and fro, forwards-backwards'),
    ("48", 'Upwards/downwards'),
    ("49", 'Variable'),
)

movManChoices = (
    ("0", 'No Value Set'),
    ("1", 'N/A'),
    ("2", 'Short'),
    ("3", 'Strong'),
    ("4", 'Slow'),
    ("5", 'Large, powerful'),
    ("6", 'Long'),
    ("7", 'Relaxed'),
    ("8", 'Trill'),
    ("9", 'Small'),
    ("10", 'Tense'),
)

contTypeChoices = (
    ("0", 'No Value Set'),
    ("1", 'N/A'),
    ("2", 'Brush'),
    ("3", 'Initial > final'),
    ("4", 'Final'),
    ("5", 'Initial'),
    ("6", 'Continuous'),
    ("7", 'Contacting hands'),
    ("8", 'Continuous + final'),
    ("9", 'None + initial'),
    ("10", '> final'),
    ("11", 'None + final'),
)

namedEntChoices = (
    ("0", 'No Value Set'),
    ("1", 'N/A'),
    ("2", 'Person'),
    ("3", 'Public figure'),
    ("4", 'Place'),
    ("5", 'Region'),
    ("6", 'Brand'),
    ("7", 'Country'),
    ("8", 'Device'),
    ("9", 'Product'),
    ("10", 'Project'),
    ("11", 'Place nickname'),
    ("12", 'Event'),
    ("13", 'Newspaper'),
    ("14", 'Story character'),
    ("15", 'Continent'),
    ("16", 'Organisation'),
    ("17", 'Company'),
    ("18", 'Team'),
    ("19", 'Drink'),
    ("20", 'Magazine'),
)


class FieldChoice(models.Model):
    field = models.CharField(max_length=50)
    english_name = models.CharField(max_length=50)
    machine_value = models.IntegerField()

    def __unicode__(self):
        return self.field + ': ' + self.english_name + ' (' + str(self.machine_value) + ')'

    class Meta:
        ordering = ['field', 'machine_value']


# This method builds a list of choices from the database
# TODO: Change this implementation to somewhere else
def build_choice_list(field):
    # These are not translated with ugettext_lazy due to json serialization problem
    choice_list = [('0', '-'), ('1', 'N/A')]

    # Try to look for fields in FieldName and choose choices from there
    try:
        for choice in FieldChoice.objects.filter(field=field):
            choice_list.append((str(choice.machine_value), choice.english_name))

        return choice_list

    # Enter this exception if for example the db has no data yet (without this it is impossible to migrate)
    except OperationalError:
        pass


class Gloss(models.Model):
    class Meta:
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
            # Translators: Gloss permissions
            ('can_publish', _('Can publish signs and definitions')),
            # Translators: Gloss permissions
            ('can_delete_unpublished',
             # Translators: Gloss permissions
             _('Can delete unpub signs or defs')),
            # Translators: Gloss permissions
            ('can_delete_published',
             # Translators: Gloss permissions
             _('Can delete pub signs and defs')),
            # Translators: Gloss permissions
            ('view_advanced_properties',
             # Translators: Gloss permissions
             _('Include all properties in sign detail view')),
        )

    def __unicode__(self):
        return "%s" % (self.idgloss)

    def field_labels(self):
        """Return the dictionary of field labels for use in a template"""

        d = dict()
        for f in self._meta.fields:
            try:
                d[f.name] = self._meta.get_field(f.name).verbose_name
            except:
                pass

        return d

    def admin_fields(self):
        """Return a list of field values in settings.ADMIN_RESULT_FIELDS 
        for use in the admin list view"""

        result = []
        for field in settings.ADMIN_RESULT_FIELDS:
            fname = self._meta.get_field(field).verbose_name

            # First, try to give the human readable choice value back
            try:
                result.append(
                    (fname, getattr(self, 'get_' + field + '_display')()))

            # If that doesn't work, give the raw value back
            except AttributeError:
                result.append((fname, getattr(self, field)))

        return result

    # Translators: Gloss models field: idgloss, verbose name
    idgloss = models.CharField(_("Gloss"), max_length=50,
                               # Translators: Help text for Gloss models field: idgloss
                               help_text=_("""
    This is the unique identifying name of an entry of a sign form in the
database. No two Sign Entry Names can be exactly the same, but a "Sign
Entry Name" can be (and often is) the same as the Annotation Idgloss."""))

    # Changed this Gloss to be for the University of Jyvaskyla folks
    # Translators: Gloss models field: annotation_idgloss_jkl, verbose name
    annotation_idgloss_jkl = models.CharField(_("Gloss JKL"), blank=True, max_length=30,
                                              # Translators: Help text for Gloss models field: annotation_idgloss_jkl
                                              help_text=_("""
    This is the Jyvaskyla name of a sign used by annotators when glossing the corpus in
an ELAN annotation file. The Jyvaskyla Annotation Idgloss may be the same for two or
more entries (each with their own 'Sign Entry Name'). If two sign entries
have the same 'Annotation Idgloss' that means they differ in form in only
minor or insignificant ways that can be ignored."""))
    # the idgloss used in transcription, may be shared between many signs

    # ID gloss for JKL Gloss' translation to English
    # Translators: Gloss models field: annotation_idgloss_jkl_en (english), verbose name
    annotation_idgloss_jkl_en = models.CharField(_("Gloss JKL (Eng)"), blank=True, max_length=30,
                                                 # Translators: Help text for Gloss models field: annotation_idgloss_jkl_en (english)
                                                 help_text=_("""
    This is the English name for the corresponding Jyvaskyla Gloss"""))

    # Changed this Gloss to be for the Helsinki folks
    # Translators: Gloss models field: annotation_idgloss_hki, verbose name
    annotation_idgloss_hki = models.CharField(_("Gloss HKI"), blank=True, max_length=30,
                                              # Translators: Help text for Gloss models field: annotation_idgloss_hki
                                              help_text=_("""
    This is the Helsinki name of a sign used by annotators when glossing the corpus in
an ELAN annotation file. The Helsinki Annotation Idgloss may be the same for two or
more entries (each with their own 'Sign Entry Name'). If two sign entries
have the same 'Annotation Idgloss' that means they differ in form in only
minor or insignificant ways that can be ignored."""))

    # ID Gloss for HKI gloss translation to English
    # Translators: Gloss models field: annotation_idgloss_hki_en (english), verbose name
    annotation_idgloss_hki_en = models.CharField(_("Gloss HKI (Eng)"), blank=True, max_length=30,
                                                 # Translators: Help text for Gloss models field: annotation_id_gloss_hki_en (english)
                                                 help_text=_("""
    This is the English name for the corresponding Jyvaskyla Gloss"""))

    # Languages that this gloss is part of
    language = models.ManyToManyField(Language)

    # Translators: Gloss models field: annotation_comments, verbose name
    annotation_comments = models.CharField(
        _("Annotation comments"), max_length=50, blank=True)

    ########

    # One or more regional dialects that this gloss is used in
    dialect = models.ManyToManyField(Dialect)
    # This field type is a guess.

    # ###
    # Translators: Gloss models field: sense, verbose name
    sense = models.IntegerField(_("Sense Number"), null=True, blank=True,
                                # Translators: Help text for Gloss models field: sense
                                help_text=_(
                                    """If there is more than one sense of a sign enter a number here,
                                       all signs with sense>1 will use the same video as sense=1"""))
    sense.list_filter_sense = True

    # TODO: See if this can be removed
    # Translators: Gloss models field: sn, verbose name
    sn = models.IntegerField(_("Sign Number"),
                             # Translators: Help text for Gloss models field: sn
                             help_text=_(
                                 "Sign Number must be a unique integer and defines the ordering of signs in the dictionary"),
                             null=True, blank=True, unique=True)
    # this is a sign number - was trying
    # to be a primary key, also defines a sequence - need to keep the sequence
    # and allow gaps between numbers for inserting later signs


    # ### Phonology fields
    # Translators: Gloss models field: handedness, verbose name
    handedness = models.CharField(_("Handedness"), blank=True, null=True, choices=build_choice_list("Handedness"),
                                  max_length=5)  # handednessChoices <- use this if you want static
    # Translators: Gloss models field: strong_handshape, verbose name
    strong_handshape = models.CharField(_("Strong Hand"), blank=True, null=True, choices=build_choice_list("Handshape"),
                                        max_length=5)
    # Translators: Gloss models field: weak_handshape, verbose name
    weak_handshape = models.CharField(_("Weak Hand"), null=True, choices=build_choice_list("Handshape"), blank=True,
                                      max_length=5)

    # Translators: Gloss models field: location, verbose name
    location = models.CharField(
        _("Location"), choices=locationChoices, null=True, blank=True,
        max_length=20)  # TODO: build_choice_list("Location")

    # Translators: Gloss models field: relatArtic, verbose name
    relatArtic = models.CharField(_("Relation between Articulators"), choices=build_choice_list("RelatArtic"),
                                  null=True,
                                  blank=True, max_length=5)

    # Translators: Gloss models field: absOriPalm, verbose name
    absOriPalm = models.CharField(_("Absolute Orientation: Palm"), choices=build_choice_list("RelatArtic"), null=True,
                                  blank=True, max_length=5)
    # Translators: Gloss models field: absOriFing, verbose name
    absOriFing = models.CharField(_("Absolute Orientation: Fingers"), choices=build_choice_list("AbsOriFing"),
                                  null=True,
                                  blank=True, max_length=5)

    # Translators: Gloss models field: relOriMov, verbose name
    relOriMov = models.CharField(_("Relative Orientation: Movement"), choices=build_choice_list("RelOriMov"), null=True,
                                 blank=True, max_length=5)
    # Translators: Gloss models field: relOriLoc, verbose name
    relOriLoc = models.CharField(_("Relative Orientation: Location"), choices=build_choice_list("RelOriLoc"), null=True,
                                 blank=True, max_length=5)
    # Translators: Gloss models field: oriCh, verbose name
    oriCh = models.CharField(_("Orientation Change"), choices=build_choice_list("OriChange"), null=True, blank=True,
                             max_length=5)

    # Translators: Gloss models field: handCh, verbose name
    handCh = models.CharField(_("Handshape Change"), choices=build_choice_list("HandshapeChange"), null=True,
                              blank=True,
                              max_length=5)

    # Translators: Gloss models field: repeat, verbose name
    repeat = models.NullBooleanField(_("Repeated Movement"), null=True, default=False)
    # Translators: Gloss models field: altern, verbose name
    altern = models.NullBooleanField(_("Alternating Movement"), null=True, default=False)

    # Translators: Gloss models field: movSh, verbose name
    movSh = models.CharField(_("Movement Shape"), choices=build_choice_list("MovementShape"), null=True, blank=True,
                             max_length=5)
    # Translators: Gloss models field: movDir, verbose name
    movDir = models.CharField(_("Movement Direction"), choices=build_choice_list("MovementDir"), null=True, blank=True,
                              max_length=5)
    # Translators: Gloss models field: movMan, verbose name
    movMan = models.CharField(_("Movement Manner"), choices=build_choice_list("MovementMan"), null=True, blank=True,
                              max_length=5)
    # Translators: Gloss models field: contType, verbose name
    contType = models.CharField(_("Contact Type"), choices=build_choice_list("ContactType"), null=True, blank=True,
                                max_length=5)

    # Translators: Gloss models field: phonOth verbose name
    phonOth = models.TextField(_("Phonology Other"), null=True, blank=True)

    # Translators: Gloss models field: mouthG, verbose name
    mouthG = models.CharField(_("Mouth Gesture"), max_length=50, blank=True)
    # Translators: Gloss models field: mouthing, verbose name
    mouthing = models.CharField(_("Mouthing"), max_length=50, blank=True)
    # Translators: Gloss models field: phonetVar, verbose name
    phonetVar = models.CharField(_("Phonetic Variation"), max_length=50, blank=True, )

    # ### Semantic fields
    # Translators: Gloss models field: iconImg, verbose name
    iconImg = models.CharField(_("Iconic Image"), max_length=50, blank=True)
    # Translators: Gloss models field: namEnt, verbose name
    namEnt = models.CharField(_("Named Entity"), choices=build_choice_list("NamedEntity"), null=True, blank=True,
                              max_length=5)
    # Translators: Gloss models field: semField, verbose name
    semField = models.CharField(_("Semantic Field"), choices=build_choice_list("SemField"), null=True, blank=True,
                                max_length=5)

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

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Gloss._meta.fields]

    def navigation(self, is_staff):
        """Return a gloss navigation structure that can be used to
        generate next/previous links from within a template page"""

        result = dict()
        result['next'] = self.next_dictionary_gloss(is_staff)
        result['prev'] = self.prev_dictionary_gloss(is_staff)
        return result

    def admin_next_gloss(self):
        """next gloss in the admin view, shortcut for next_dictionary_gloss with staff=True"""

        return self.next_dictionary_gloss(True)

    def admin_prev_gloss(self):
        """previous gloss in the admin view, shortcut for prev_dictionary_gloss with staff=True"""

        return self.prev_dictionary_gloss(True)

    # TODO: See if this is really needed, 'sn' seems like a dirty way to determine order
    def next_dictionary_gloss(self, staff=False):
        """Find the next gloss in dictionary order"""
        if self.sn == None:
            return None
        elif staff:
            set = Gloss.objects.filter(sn__gt=self.sn).order_by('sn')
        else:
            set = Gloss.objects.filter(
                sn__gt=self.sn, in_web_dictionary__exact=True).order_by('sn')
        if set:
            return set[0]
        else:
            return None

    # TODO: See if this is really needed, 'sn' seems like a dirty way to determine order
    def prev_dictionary_gloss(self, staff=False):
        """Find the previous gloss in dictionary order"""
        if self.sn == None:
            return None
        elif staff:
            set = Gloss.objects.filter(sn__lt=self.sn).order_by('-sn')
        else:
            set = Gloss.objects.filter(
                sn__lt=self.sn, in_web_dictionary__exact=True).order_by('-sn')
        if set:
            return set[0]
        else:
            return None

    def get_absolute_url(self):
        return "/dictionary/gloss/%s.html" % self.idgloss

    def homophones(self):
        """Return the set of homophones for this gloss ordered by sense number"""

        if self.sense == 1:
            relations = Relation.objects.filter(
                role="homophone", target__exact=self).order_by('source__sense')
            homophones = [rel.source for rel in relations]
            homophones.insert(0, self)
            return homophones
        elif self.sense > 1:
            # need to find the root and see how many senses it has
            homophones = self.relation_sources.filter(
                role='homophone', target__sense__exact=1)
            if len(homophones) > 0:
                root = homophones[0].target
                return root.homophones()
        return []

    def get_video_gloss(self):
        """Work out the gloss that might have the video for this sign, usually the sign number but
        if we're a sense>1 then we look at the homophone with sense=1
        Return the gloss instance."""

        if self.sense > 1:
            homophones = self.relation_sources.filter(
                role='homophone', target__sense__exact=1)
            # should be only zero or one of these
            if len(homophones) > 0:
                return homophones[0].target
        return self

    def get_video(self):
        """Return the video object for this gloss or None if no video available"""

        video_path = 'glossvideo/' + \
                     unicode(self.idgloss[:2]) + '/' + unicode(self.idgloss) + '-' + unicode(self.pk) + '.mp4'

        if os.path.isfile(settings.MEDIA_ROOT + '/' + video_path):
            return video_path
        else:
            return None

        # TODO: Find out the mystery of this line, it is unreachable
        video_with_gloss = self.get_video_gloss()

        try:
            video = video_with_gloss.glossvideo_set.get(version__exact=0)
            return video
        except:
            return None

    def count_videos(self):
        """Return a count of the number of videos we have 
        for this video - ie. the number of versions stored"""

        video_with_gloss = self.get_video_gloss()

        return video_with_gloss.glossvideo_set.count()

    def get_video_url(self):
        """Return  the url of the video for this gloss which may be that of a homophone"""

        return '/home/wessel/signbank/signbank/video/testmedia/AANBELLEN-320kbits.mp4'  # TODO: Remove this line?

        # TODO: Unreachable line
        video = self.get_video()
        if video != None:
            return video.get_absolute_url()
        else:
            return ""

    def has_video(self):
        """Test to see if the video for this sign is present"""

        return self.get_video() != None

    def published_definitions(self):
        """Return a query set of just the published definitions for this gloss
        also filter out those fields not in DEFINITION_FIELDS"""

        defs = self.definition_set.filter(published__exact=True)

        return [d for d in defs if d.role in settings.DEFINITION_FIELDS]

    def definitions(self):
        """Gather together the definitions for this gloss"""

        defs = dict()
        for d in self.definition_set.all().order_by('count'):
            if not defs.has_key(d.role):
                defs[d.role] = []

            defs[d.role].append(d.text)
        return defs

    def options_to_json(self, options):
        """Convert an options list to a json dict"""

        result = []
        for k, v in options:
            result.append('"%s":"%s"' % (k, v))
        return "{" + ",".join(result) + "}"

    def handshape_choices_json(self):
        """Return JSON for the handshape choice list"""

        return self.options_to_json(handshapeChoices)

    def location_choices_json(self):
        """Return JSON for the location choice list"""

        return self.options_to_json(locationChoices)

    def palm_orientation_choices_json(self):
        """Return JSON for the palm orientation choice list"""

        return self.options_to_json(palmOrientationChoices)

    def relative_orientation_choices_json(self):
        """Return JSON for the relative orientation choice list"""

        return self.options_to_json(relOrientationChoices)

    def secondary_location_choices_json(self):  # TODO: see if these can be removed
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

    def dialect_choices(self):
        """Return JSON for dialect choices"""

        d = dict()
        for l in Dialect.objects.all():
            d[l.name] = l.name

        return json.dumps(d)

    def get_choice_lists(self):
        """Return JSON for the location choice list"""

        choice_lists = {}

        # Start with your own choice lists
        for fieldname in ['handedness', 'location', 'strong_handshape', 'weak_handshape',
                          'relatArtic', 'absOriPalm', 'absOriFing', 'relOriMov',
                          'relOriLoc', 'handCh', 'repeat', 'altern', 'movSh',
                          'movDir', 'movMan', 'contType', 'namEnt', 'oriCh', 'semField']:
            # Get the list of choices for this field
            li = self._meta.get_field(fieldname).choices

            # Sort the list
            sorted_li = sorted(li, key=lambda x: x[1])

            # Put it in another format
            reformatted_li = [('_' + str(value), text)
                              for value, text in sorted_li]
            choice_lists[fieldname] = OrderedDict(reformatted_li)

        # Choice lists for other models
        choice_lists['morphology_role'] = [human_value for machine_value, human_value in
                                           build_choice_list('MorphologyType')]

        return json.dumps(choice_lists)

# Register Gloss for tags
try:
    tagging.register(Gloss)
except tagging.AlreadyRegistered:
    pass

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
    role = models.CharField(max_length=20, choices=build_choice_list('MorphologyType'))
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
    # ('MorphologyType'))
    role = models.CharField(max_length=5, choices=(
        # Translators: Role choice for MorphologyDefinition
        ('0', _('-')),
        # Translators: Role choice for MorphologyDefinition
        ('1', _('N/A'))))
    morpheme = models.ForeignKey(Gloss, related_name="morphemes")

    def __unicode__(self):
        return unicode(self.morpheme.idgloss) + ' is ' + unicode(self.get_role_display()) + ' of ' + unicode(self.parent_gloss.idgloss)
