# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import OperationalError, ProgrammingError
from django.utils.translation import ugettext_lazy as _
from tagging.models import Tag

from .models import (AllowedTags, Dataset, FieldChoice, Gloss, GlossRelation,
                     GlossURL, Language, MorphologyDefinition, Relation,
                     RelationToForeignSign, SignLanguage)


class GlossCreateForm(forms.ModelForm):
    """
    Form for creating a new gloss.
    This form also overrides the ModelForm validations.
    """
    dataset = forms.ModelChoiceField(label=_('Dataset'), required=True, queryset=Dataset.objects.all(), empty_label=None)
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except (ObjectDoesNotExist, OperationalError, ProgrammingError):
        qs = Tag.objects.all()
    tag = forms.ModelChoiceField(queryset=qs, required=False, empty_label="---", to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_idgloss(self):
        """Validates that idgloss is unique in Dataset."""
        try:
            gloss = Gloss.objects.get(idgloss__exact=self.cleaned_data['idgloss'], dataset=self.cleaned_data['dataset'])
        except Gloss.DoesNotExist:
            return self.cleaned_data['idgloss']
        raise forms.ValidationError(
            # Translators: exception ValidationError
            _('This Gloss value already exists in the chosen Dataset. Please choose another value for Gloss.'),
            code='not_unique')

    class Meta:
        model = Gloss
        fields = ['dataset', 'idgloss', 'idgloss_mi', ]


class TagUpdateForm(forms.Form):
    """Form to add a new tag to a gloss"""
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except (ObjectDoesNotExist, OperationalError, ProgrammingError):
        qs = Tag.objects.all()
    tag = forms.ModelChoiceField(queryset=qs, empty_label=None, to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}))


class TagDeleteForm(forms.Form):
    """Form to delete a tag from a gloss"""
    tag = forms.ModelChoiceField(queryset=Tag.objects.all(), empty_label=None, to_field_name='name')
    delete = forms.BooleanField(required=True, widget=forms.HiddenInput)


class TagsAddForm(forms.Form):
    """Form to add a new tags to a gloss"""
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except (ObjectDoesNotExist, OperationalError, ProgrammingError):
        qs = Tag.objects.all()
    tags = forms.ModelMultipleChoiceField(label=_('Tags'), queryset=qs, to_field_name='name')


ATTRS_FOR_FORMS = {'class': 'form-control'}


def build_related_to_choices():
    related_to = [(None, '---------')]
    qs = RelationToForeignSign.objects.order_by().distinct().values_list('other_lang', flat=True)
    for i in range(len(qs)):
        val = (qs[i], qs[i])
        related_to.append(val)

    return related_to


class GlossSearchForm(forms.ModelForm):
    # Translators: GlossSearchForm label
    dataset = forms.ModelMultipleChoiceField(label=_('Dataset'), queryset=Dataset.objects.all(), required=False)

    search = forms.CharField(label=_("Search"))
    # Translators: GlossSearchForm label
    gloss = forms.CharField(label=_("Gloss"))
    # Translators: GlossSearchForm label
    idgloss_mi = forms.CharField(label=_("Gloss in Māori"))
    # Translators: GlossSearchForm label
    keyword = forms.CharField(label=_('Translations'))
    # Translators: GlossSearchForm label
    trans_lang = forms.ModelChoiceField(required=False, empty_label=_('Choose language'), queryset=Language.objects.all())

    # Adding topics
    semantic_field = forms.ModelMultipleChoiceField(label=_('Topic'), queryset=FieldChoice.objects.filter(field='semantic_field'),
                                            required=False)

    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except (ObjectDoesNotExist, OperationalError, ProgrammingError):
        qs = Tag.objects.all()
    tags = forms.ModelMultipleChoiceField(queryset=qs, required=False)
    nottags = forms.ModelMultipleChoiceField(queryset=qs)

    published = forms.BooleanField(label=_('Is published'), required=False)

    # Translators: GlossSearchForm label
    hasvideo = forms.BooleanField(label=_('Has videos'), required=False)
    hasnovideo = forms.BooleanField(label=_('No videos'), required=False)
    multiplevideos = forms.BooleanField(label=_('Multiple videos'), required=False)

    relation_to_foreign_signs = forms.ChoiceField(label=_('Relation to foreign signs'), choices=build_related_to_choices,
                                                  required=False, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Adding usage
    usage = forms.ModelMultipleChoiceField(label=_('Usage'), queryset=FieldChoice.objects.filter(field='usage'),
                                           required=False)
    location = forms.ModelChoiceField(label=_('Location'), queryset=FieldChoice.objects.filter(field='location'),
                                      to_field_name='machine_value', required=False)
                                      
    age_variation = forms.ModelChoiceField(label=_('Age Variation'), queryset=FieldChoice.objects.filter(field='age_variation'),
                                           to_field_name='machine_value', required=False)                                        
    example_search = forms.CharField(label=_('Example Field search'), required=False)
    strong_handshape = forms.ModelChoiceField(label=_('Strong handshape'), queryset=FieldChoice.objects.filter(field='strong_handshape'),
                                              to_field_name='machine_value', required=False)
    one_or_two_handed = forms.BooleanField(label=_('One or two handed'), required=False)
    word_classes = forms.ModelMultipleChoiceField(label=_('Word classes'),
                                                  queryset=FieldChoice.objects.filter(field='wordclass'),
                                                  required=False)
    handedness = forms.ModelChoiceField(label=_('Handedness'), queryset=FieldChoice.objects.filter(field='handedness'),
                                        to_field_name='machine_value', required=False)

    # Adding morphology fields
    number_incorporated = forms.BooleanField(label=_('Number incorporated'), required=False)
    locatable = forms.BooleanField(label=_('Locatable'), required=False)
    directional = forms.BooleanField(label=_('Directional'), required=False)
    fingerspelling = forms.BooleanField(label=_('Fingerspelling'), required=False)
    inflection_temporal = forms.BooleanField(label=_('Inflection: Temporal'), required=False)
    inflection_manner_degree = forms.BooleanField(label=_('Inflection: Manner and Degree'), required=False)
    inflection_plural = forms.BooleanField(label=_('Inflection: Plural'), required=False)

    # These have been disabled until they are later needed
    # TODO: To enable these, uncomment them.
    """
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
    phonology_other = forms.CharField(
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

    # Translators: GlossSearchForm label
    repeated_movement = forms.ChoiceField(
        label=_('Repeating Movement'), choices=NULLBOOLEANCHOICES)
    # ,widget=forms.Select(attrs=ATTRS_FOR_FORMS));
    # Translators: GlossSearchForm label
    alternating_movement = forms.ChoiceField(
        label=_('Alternating Movement'), choices=NULLBOOLEANCHOICES)
    """

    class Meta:
        ATTRS_FOR_FORMS = {'class': 'form-control'}

        model = Gloss
        fields = ('idgloss', 'idgloss_mi', 'dialect', 'strong_handshape', 'weak_handshape', 'location',
                  'handedness', 'notes', 'relation_between_articulators', 'absolute_orientation_palm',
                  'absolute_orientation_fingers', 'relative_orientation_movement', 'relative_orientation_location',
                  'orientation_change', 'handshape_change', 'repeated_movement', 'alternating_movement',
                  'movement_shape', 'movement_direction', 'movement_manner', 'contact_type', 'mouth_gesture',
                  'mouthing', 'phonetic_variation', 'iconic_image', 'named_entity', 'semantic_field',
                  'number_of_occurences',)


class GlossRelationSearchForm(forms.Form):
    # Translators: GlossSearchForm label
    dataset = forms.ModelMultipleChoiceField(label=_('Dataset'), queryset=Dataset.objects.all(), required=False)
    search = forms.CharField(label=_("Search"))
    # Translators: GlossSearchForm label
    source = forms.CharField(label=_("Source Gloss"))
    # Translators: GlossSearchForm label
    target = forms.CharField(label=_("Target Gloss"))

    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(GlossRelation)).allowed_tags.all()
    except (ObjectDoesNotExist, OperationalError, ProgrammingError):
        qs = Tag.objects.all()
    tags = forms.ModelMultipleChoiceField(queryset=qs, required=False, label=_("Relation type"))

    class Meta:
        ATTRS_FOR_FORMS = {'class': 'form-control'}


class GlossRelationForm(forms.Form):
    source = forms.CharField(widget=forms.HiddenInput())
    target = forms.CharField(label=_("Gloss"), widget=forms.TextInput(
        attrs={'class': 'glossrelation-autocomplete'}))
    tag = forms.ModelChoiceField(label=_("Relation type:"),
                                 queryset=AllowedTags.objects.none(),
                                 required=True, to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    delete = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_tag = AllowedTags.objects.filter(
            content_type=ContentType.objects.get_for_model(GlossRelation)).first()
        if allowed_tag:
            self.fields['tag'].queryset = allowed_tag.allowed_tags.all()


class GlossURLForm(forms.ModelForm):
    class Meta:
        model = GlossURL
        fields = ["gloss", "url"]


class RelationForm(forms.ModelForm):
    # Translators: RelationForm label
    sourceid = forms.CharField(label=_('Source Gloss'))
    # Translators: RelationForm label
    targetid = forms.CharField(label=_('Target Gloss'))
    # Note that to_field_name has to be unique!
    role = forms.ModelChoiceField(label=_('Type'), queryset=FieldChoice.objects.filter(field='MorphologyType'),
                                  to_field_name='machine_value', empty_label=None,
                                  widget=forms.Select(attrs=ATTRS_FOR_FORMS))

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
    # role = forms.ChoiceField(label=_('Type'), choices=build_choice_list(
    #    'MorphologyType'), widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    # Note that to_field_name has to be unique!
    role = forms.ModelChoiceField(label=_('Type'), queryset=FieldChoice.objects.filter(field='MorphologyType'),
                                  to_field_name='machine_value', empty_label=None,
                                  widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    # role = forms.ChoiceField(label=_('Type'), widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: MorphologyForm label
    morpheme_id = forms.CharField(label=_('Morpheme'))

    class Meta:
        model = MorphologyDefinition
        fields = ['role']


class CSVUploadForm(forms.Form):
    file = forms.FileField()
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all(), empty_label=None)

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError(_('Must be a CSV file with .csv extension.'))
        return file


class DatasetMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Override the field used for the label."""
    def label_from_instance(self, obj):
        return obj.public_name


class GlossPublicSearchForm(forms.Form):
    """Public search form."""
    gloss = forms.CharField(label=_("Search gloss"), required=False,
                             widget=forms.TextInput(attrs={'placeholder': _('Search gloss')}))
    keyword = forms.CharField(label=_("Search translation equivalent"), required=False,
                             widget=forms.TextInput(attrs={'placeholder': _('Search translation equivalent')}))
    try:
        signlang_qs = SignLanguage.objects.filter(
                id__in=[x.signlanguage.id for x in Dataset.objects.filter(is_public=True)])
    except:
        signlang_qs = SignLanguage.objects.none()
    lang = forms.ModelChoiceField(
        queryset=signlang_qs,
        to_field_name="language_code_3char", empty_label=_("All sign languages"), required=False,
        label=_("Sign language"))
    dataset = DatasetMultipleChoiceField(queryset=Dataset.objects.filter(is_public=True), required=False,
                                         label=_("You can restrict your search to these lexicons"),
                                         widget=forms.CheckboxSelectMultiple())


class LexiconForm(forms.Form):
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all())