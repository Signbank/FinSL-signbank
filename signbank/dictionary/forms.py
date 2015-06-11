from django import forms
from formtools.preview import FormPreview
from signbank.video.fields import VideoUploadToFLVField
from signbank.dictionary.models import Dialect, Gloss, Definition, Relation, RelationToForeignSign, MorphologyDefinition, DEFN_ROLE_CHOICES, build_choice_list
from django.conf import settings
from tagging.models import Tag
from django.utils.translation import ugettext_lazy as _

# TODO: Check what this is?
# category choices are tag values that we'll restrict search to
CATEGORY_CHOICES = (('all', _('All Signs')),
                    ('semantic:health', _('Only Health Related Signs')),
                    ('semantic:education', _('Only Education Related Signs')))


class UserSignSearchForm(forms.Form):

    glossQuery = forms.CharField(label=_('Glosses containing'), max_length=100,
                                 required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    query = forms.CharField(label=_('Translations containing'), max_length=100,
                            required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
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
        fields = ['idgloss', 'annotation_idgloss_jkl', 'annotation_idgloss_jkl_en', 'annotation_idgloss_hki', 'annotation_idgloss_hki_en']


class VideoUpdateForm(forms.Form):

    """Form to allow update of the video for a sign"""
    videofile = VideoUploadToFLVField()


class TagUpdateForm(forms.Form):

    """Form to add a new tag to a gloss"""

    tag = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),
                            choices=[(t, t) for t in settings.ALLOWED_TAGS])
    delete = forms.BooleanField(required=False, widget=forms.HiddenInput)

YESNOCHOICES = (("unspecified", _("Unspecified")), ('yes', _('Yes')), ('no', _('No')))
NULLBOOLEANCHOICES = [
    (0, '---------'), (1, _('Unknown')), (2, _('True')), (3, _('False'))]

RELATION_ROLE_CHOICES = (('', '---------'),
                         ('all', _('All')),
                         ('homonym', _('Homonym')),
                         ('synonym', _('Synonym')),
                         ('variant', _('Variant')),
                         ('antonym', _('Antonym')),
                         ('hyponym', _('Hyponym')),
                         ('hypernym', _('Hypernym')),
                         ('seealso', _('See Also')),
                         )

DEFN_ROLE_CHOICES = (('', '---------'), ('all', _('All'))) + DEFN_ROLE_CHOICES
MORPHEME_ROLE_CHOICES = [
    ('', '---------')] + build_choice_list('MorphologyType')
ATTRS_FOR_FORMS = {'class': 'form-control'}


class GlossSearchForm(forms.ModelForm):

    search = forms.CharField(label=_("JKL Gloss"))
    JKLenglishGloss = forms.CharField(label=_("JKL English Gloss"))
    HKIGloss = forms.CharField(label=_("HKI Gloss"))
    HKIenglishGloss = forms.CharField(label=_("HKI English Gloss"))
    tags = forms.MultipleChoiceField(
        choices=[(t, t) for t in settings.ALLOWED_TAGS])
    nottags = forms.MultipleChoiceField(
        choices=[(t, t) for t in settings.ALLOWED_TAGS])
    keyword = forms.CharField(label=_('Translations'))
    hasvideo = forms.ChoiceField(label=_('Has Video'), choices=YESNOCHOICES)
    defspublished = forms.ChoiceField(
        label=_("All Definitions Published"), choices=YESNOCHOICES)

    defsearch = forms.CharField(label=_('Search Definition/Notes'))
    #defrole = forms.ChoiceField(label='Search Definition/Note Type', choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    relation = forms.CharField(
        label=_('Search for gloss of related signs'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))
    relationToForeignSign = forms.CharField(
        label=_('Search for gloss of foreign signs'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))
    morpheme = forms.CharField(
        label=_('Search for gloss with this as morpheme'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))

    phonOth = forms.CharField(
        label=_('Phonology other'), widget=forms.TextInput())

    hasRelationToForeignSign = forms.ChoiceField(label=_('Related to foreign sign or not'), choices=[
                                                 (0, '---------'), (1, _('Yes')), (2, _('No'))], widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    hasRelation = forms.ChoiceField(
        label=_('Type of relation'), choices=RELATION_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    hasMorphemeOfType = forms.ChoiceField(
        label=_('Has morpheme type'), choices=MORPHEME_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    # ,widget=forms.Select(attrs=ATTRS_FOR_FORMS));
    repeat = forms.ChoiceField(
        label=_('Repeating Movement'), choices=NULLBOOLEANCHOICES)
    # ,widget=forms.Select(attrs=ATTRS_FOR_FORMS));
    altern = forms.ChoiceField(
        label=_('Alternating Movement'), choices=NULLBOOLEANCHOICES)

    isNew = forms.ChoiceField(
        label=_('Is a proposed new sign'), choices=NULLBOOLEANCHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    inWeb = forms.ChoiceField(
        label=_('Is in Web dictionary'), choices=NULLBOOLEANCHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    definitionRole = forms.ChoiceField(
        label=_('Note type'), choices=DEFN_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    definitionContains = forms.CharField(
        label=_('Note contains'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))

    class Meta:

        ATTRS_FOR_FORMS = {'class': 'form-control'}

        model = Gloss
        fields = ('idgloss', 'annotation_idgloss_jkl', 'annotation_idgloss_jkl_en', 'annotation_idgloss_hki', 'annotation_idgloss_hki_en', 'morph', 'sense',
                  'sn', 'StemSN', 'comptf', 'compound', 'language', 'dialect',
                  'inWeb', 'isNew',
                  'initial_relative_orientation', 'final_relative_orientation',
                  'initial_palm_orientation', 'final_palm_orientation',
                  'initial_secondary_loc', 'final_secondary_loc',
                  'domhndsh', 'subhndsh', 'locprim', 'locVirtObj', 'locsecond',
                  'final_domhndsh', 'final_subhndsh', 'final_loc',

                  'handedness', 'useInstr', 'rmrks', 'relatArtic', 'absOriPalm', 'absOriFing',
                  'relOriMov', 'relOriLoc', 'oriCh', 'handCh', 'repeat', 'altern', 'movSh', 'movDir', 'movMan', 'contType', 'mouthG',
                  'mouthing', 'phonetVar', 'iconImg', 'namEnt', 'semField',
                  'tokNoA', 'tokNoSgnrA', 'tokNoV', 'tokNoSgnrV', 'tokNoR', 'tokNoSgnrR', 'tokNoGe', 'tokNoSgnrGe',
                  'tokNoGr', 'tokNoSgnrGr', 'tokNoO', 'tokNoSgnrO')


class DefinitionForm(forms.ModelForm):

    class Meta:
        model = Definition
        fields = ('published', 'count', 'role', 'text')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class RelationForm(forms.ModelForm):

    sourceid = forms.CharField(label=_('Source Gloss'))
    targetid = forms.CharField(label=_('Target Gloss'))

    class Meta:
        model = Relation
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class RelationToForeignSignForm(forms.ModelForm):

    sourceid = forms.CharField(label=_('Source Gloss'))
    #loan = forms.CharField(label='Loan')
    other_lang = forms.CharField(label=_('Related Language'))
    other_lang_gloss = forms.CharField(label=_('Gloss in Related Language'))

    class Meta:
        model = RelationToForeignSign
        fields = ['loan', 'other_lang', 'other_lang_gloss']
        widgets = {}


class MorphologyForm(forms.ModelForm):

    parent_gloss_id = forms.CharField(label=_('Parent Gloss'))
    role = forms.ChoiceField(label=_('Type'), choices=build_choice_list(
        'MorphologyType'), widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    morpheme_id = forms.CharField(label=_('Morpheme'))

    class Meta:
        model = MorphologyDefinition
        fields = ['role']


class CSVUploadForm(forms.Form):

    file = forms.FileField()
