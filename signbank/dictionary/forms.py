from django import forms
from formtools.preview import FormPreview
from signbank.video.fields import VideoUploadToFLVField
from signbank.dictionary.models import Dialect, Gloss, Definition, Relation, RelationToForeignSign, \
    MorphologyDefinition, DEFN_ROLE_CHOICES, build_choice_list
from django.conf import settings
from tagging.models import Tag
from django.utils.translation import ugettext_lazy as _

# TODO: Check what this is?
# category choices are tag values that we'll restrict search to
CATEGORY_CHOICES = (
    # Translators: These are CATEGORY_CHOICES
    ('all', _('All Signs')),
    # Translators: These are CATEGORY_CHOICES
    ('semantic:health', _('Only Health Related Signs')),
    # Translators: These are CATEGORY_CHOICES
    ('semantic:education', _('Only Education Related Signs'))
)


class UserSignSearchForm(forms.Form):
    # Translators: UserSignSearchForm
    glossQuery = forms.CharField(label=_('Glosses containing'), max_length=100,
                                 required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Translators: UserSignSearchForm
    query = forms.CharField(label=_('Translations containing'), max_length=100,
                            required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Translators: UserSignSearchForm
    category = forms.ChoiceField(label=_('Search'), choices=CATEGORY_CHOICES,
                                 required=False, widget=forms.Select(attrs={'class': 'form-control'}))


class GlossModelForm(forms.ModelForm):
    class Meta:
        model = Gloss
        # fields are defined in settings.py
        fields = settings.QUICK_UPDATE_GLOSS_FIELDS


class GlossCreateForm(forms.ModelForm):
    """Form for creating a new gloss from scratch"""

    class Meta:
        model = Gloss
        fields = ['idgloss', 'annotation_idgloss_jkl', 'annotation_idgloss_jkl_en', 'annotation_idgloss_hki',
                  'annotation_idgloss_hki_en']


class VideoUpdateForm(forms.Form):
    """Form to allow update of the video for a sign"""
    videofile = VideoUploadToFLVField()


class TagUpdateForm(forms.Form):
    """Form to add a new tag to a gloss"""

    tag = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),
                            choices=[(t, t) for t in settings.ALLOWED_TAGS])
    delete = forms.BooleanField(required=False, widget=forms.HiddenInput)


YESNOCHOICES = (
    # Translators: YESNOCHOICES
    ("unspecified", _("Unspecified")),
    # Translators: YESNOCHOICES
    ('yes', _('Yes')),
    # Translators: YESNOCHOICES
    ('no', _('No')))
NULLBOOLEANCHOICES = [
    (0, '---------'),
    # Translators: YESNOCHOICES
    (1, _('Unknown')),
    # Translators: YESNOCHOICES
    (2, _('True')),
    # Translators: YESNOCHOICES
    (3, _('False'))]

RELATION_ROLE_CHOICES = (('', '---------'),
                         # Translators: RELATION_ROLE_CHOICES
                         ('all', _('All')),
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

DEFN_ROLE_CHOICES = (('', '---------'),
                     # Translators: DEFN_ROLE_CHOICES
                     ('all', _('All'))) + DEFN_ROLE_CHOICES
MORPHEME_ROLE_CHOICES = [
                            ('', '---------')] + build_choice_list('MorphologyType')
ATTRS_FOR_FORMS = {'class': 'form-control'}


class GlossSearchForm(forms.ModelForm):
    # Translators: GlossSearchForm label
    search = forms.CharField(label=_("Gloss JKL"))
    # Translators: GlossSearchForm label
    JKLenglishGloss = forms.CharField(label=_("Gloss JKL English"))
    # Translators: GlossSearchForm label
    HKIGloss = forms.CharField(label=_("Gloss HKI"))
    # Translators: GlossSearchForm label
    HKIenglishGloss = forms.CharField(label=_("Gloss HKI English"))
    tags = forms.MultipleChoiceField(
        choices=[(t, t) for t in settings.ALLOWED_TAGS])
    nottags = forms.MultipleChoiceField(
        choices=[(t, t) for t in settings.ALLOWED_TAGS])
    # Translators: GlossSearchForm label
    keyword = forms.CharField(label=_('Translations'))
    # Translators: GlossSearchForm label
    hasvideo = forms.ChoiceField(label=_('Has Video'), choices=YESNOCHOICES)
    # Translators: GlossSearchForm label
    defspublished = forms.ChoiceField(
        label=_("All Definitions Published"), choices=YESNOCHOICES)
    # Translators: GlossSearchForm label
    defsearch = forms.CharField(label=_('Search Definition/Notes'))
    # defrole = forms.ChoiceField(label='Search Definition/Note Type', choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    # Translators: GlossSearchForm label
    relation = forms.CharField(
        label=_('Search for gloss of related signs'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    relationToForeignSign = forms.CharField(
        label=_('Search for gloss of foreign signs'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    morpheme = forms.CharField(
        label=_('Search for gloss with this as morpheme'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))

    # Translators: GlossSearchForm label
    phonOth = forms.CharField(
        label=_('Phonology other'), widget=forms.TextInput())

    # Translators: GlossSearchForm label
    hasRelationToForeignSign = forms.ChoiceField(label=_('Related to foreign sign or not'), choices=[
        (0, '---------'), (1, _('Yes')), (2, _('No'))], widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    hasRelation = forms.ChoiceField(
        label=_('Type of relation'), choices=RELATION_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    hasMorphemeOfType = forms.ChoiceField(
        label=_('Has morpheme type'), choices=MORPHEME_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    # ,widget=forms.Select(attrs=ATTRS_FOR_FORMS));
    # Translators: GlossSearchForm label
    repeat = forms.ChoiceField(
        label=_('Repeating Movement'), choices=NULLBOOLEANCHOICES)
    # ,widget=forms.Select(attrs=ATTRS_FOR_FORMS));
    # Translators: GlossSearchForm label
    altern = forms.ChoiceField(
        label=_('Alternating Movement'), choices=NULLBOOLEANCHOICES)

    # Translators: GlossSearchForm label
    is_proposed_new_sign = forms.ChoiceField(
        label=_('Is a proposed new sign'), choices=NULLBOOLEANCHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    in_web_dictionary = forms.ChoiceField(
        label=_('Is in Web dictionary'), choices=NULLBOOLEANCHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    definitionRole = forms.ChoiceField(
        label=_('Note type'), choices=DEFN_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    definitionContains = forms.CharField(
        label=_('Note contains'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))

    class Meta:
        ATTRS_FOR_FORMS = {'class': 'form-control'}

        model = Gloss
        fields = ('idgloss', 'annotation_idgloss_jkl', 'annotation_idgloss_jkl_en', 'annotation_idgloss_hki',
                  'annotation_idgloss_hki_en', 'sense',
                  'sn', 'language', 'dialect',
                  'in_web_dictionary', 'is_proposed_new_sign',
                  'strong_handshape', 'weak_handshape', 'location',

                  'handedness', 'annotation_comments', 'relatArtic', 'absOriPalm', 'absOriFing',
                  'relOriMov', 'relOriLoc', 'oriCh', 'handCh', 'repeat', 'altern', 'movSh', 'movDir', 'movMan',
                  'contType', 'mouthG',
                  'mouthing', 'phonetVar', 'iconImg', 'namEnt', 'semField', 'number_of_occurences')


class DefinitionForm(forms.ModelForm):
    class Meta:
        model = Definition
        fields = ('published', 'count', 'role', 'text')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class RelationForm(forms.ModelForm):
    # Translators: RelationForm label
    sourceid = forms.CharField(label=_('Source Gloss'))
    # Translators: RelationForm label
    targetid = forms.CharField(label=_('Target Gloss'))

    class Meta:
        model = Relation
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class RelationToForeignSignForm(forms.ModelForm):
    # Translators: RelationToForeignSignForm label
    sourceid = forms.CharField(label=_('Source Gloss'))
    # loan = forms.CharField(label='Loan')
    # Translators: RelationToForeignSignForm label
    other_lang = forms.CharField(label=_('Related Language'))
    # Translators: RelationToForeignSignForm label
    other_lang_gloss = forms.CharField(label=_('Gloss in Related Language'))

    class Meta:
        model = RelationToForeignSign
        fields = ['loan', 'other_lang', 'other_lang_gloss']
        widgets = {}


class MorphologyForm(forms.ModelForm):
    # Translators: MorphologyForm label
    parent_gloss_id = forms.CharField(label=_('Parent Gloss'))
    role = forms.ChoiceField(label=_('Type'), choices=build_choice_list(
        'MorphologyType'), widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: MorphologyForm label
    morpheme_id = forms.CharField(label=_('Morpheme'))

    class Meta:
        model = MorphologyDefinition
        fields = ['role']


class CSVUploadForm(forms.Form):
    file = forms.FileField()
