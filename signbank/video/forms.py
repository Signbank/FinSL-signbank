# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from signbank.dictionary.models import Dataset, FieldChoice, Gloss

from .models import GlossVideo


class GlossVideoForm(forms.ModelForm):
    """Form for GlossVideo."""

    def __init__(self, *args, **kwargs):
        super(GlossVideoForm, self).__init__(*args, **kwargs)
        # Form is used in gloss creation, support creating a gloss without a video.
        self.fields['videofile'].required = False

    def clean_videofile(self):
        # Checking here that the file ends with .mp4
        if self.cleaned_data['videofile'] and not self.cleaned_data['videofile'].name.endswith('.mp4'):
            raise forms.ValidationError(
                'File is not a mp4. Please upload only mp4 files')
        return self.cleaned_data['videofile']

    class Meta:
        model = GlossVideo
        fields = ["title", "videofile"]


class GlossVideoForGlossForm(forms.ModelForm):
    """Form for GlossVideo with Gloss."""
    redirect = forms.CharField(widget=forms.HiddenInput, required=False)
    webcam = forms.BooleanField(required=False)
    video_type = forms.ModelChoiceField(label=_('Type'), queryset=FieldChoice.objects.filter(field='video_type'),
                                        to_field_name='machine_value', empty_label=None, required=True,
                                        widget=forms.Select(attrs={'required': True}))

    class Meta:
        model = GlossVideo
        fields = ["title", "videofile", "gloss", "video_type"]


class GlossVideoUpdateForm(forms.ModelForm):
    """Form for adding Gloss and Dataset to GlossVideo."""
    gloss = forms.ModelChoiceField(
        queryset=Gloss.objects.none(),
        widget=forms.TextInput(attrs={
            'required': True,
            'id': 'id_gloss',
            'class': 'gloss-autocomplete'}))
    video_type = forms.ModelChoiceField(label=_('Type'), queryset=FieldChoice.objects.filter(field='video_type'),
                                        to_field_name='machine_value', empty_label=None, required=True,
                                        widget=forms.Select(attrs={'required': True}))

    class Meta:
        model = GlossVideo
        fields = ['dataset', 'videofile', 'gloss', 'video_type']


class MultipleVideoUploadForm(forms.Form):
    """Form for uploading multiple videos."""
    file_field = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True, 'onchange': 'updateSize();'}))
    dataset = forms.ModelChoiceField(
        queryset=Dataset.objects.all(), required=True, empty_label=None)

    def clean_file_field(self):
        data = self.cleaned_data['file_field']
        return data


class GlossVideoPosterForm(forms.ModelForm):
    class Meta:
        model = GlossVideo
        fields = ['posterfile', 'id']
