# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import GlossVideo
from signbank.dictionary.models import Dataset, Gloss


class GlossVideoForm(forms.ModelForm):
    """Form for GlossVideo."""
    def __init__(self, *args, **kwargs):
        super(GlossVideoForm, self).__init__(*args, **kwargs)
        # Form is used in gloss creation, support creating a gloss without a video.
        self.fields['videofile'].required = False

    def clean_videofile(self):
        # Checking here that the file ends with .mp4
        if self.cleaned_data['videofile'] and not self.cleaned_data['videofile'].name.endswith('.mp4'):
            raise forms.ValidationError('File is not a mp4. Please upload only mp4 files')
        return self.cleaned_data['videofile']

    class Meta:
        model = GlossVideo
        fields = ["title", "videofile"]


class GlossVideoForGlossForm(forms.ModelForm):
    """Form for GlossVideo with Gloss."""
    redirect = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = GlossVideo
        fields = ["title", "videofile", "gloss"]


class GlossVideoUpdateForm(forms.ModelForm):
    """Form for adding Gloss and Dataset to GlossVideo."""
    gloss = forms.ModelChoiceField(queryset=Gloss.objects.none(), widget=forms.TextInput)

    class Meta:
        model = GlossVideo
        fields = ['dataset', 'videofile', 'gloss']


class MultipleVideoUploadForm(forms.Form):
    """Form for uploading multiple videos."""
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'onchange': 'updateSize();'}))
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all(), required=True, empty_label=None)

    def clean_file_field(self):
        data = self.cleaned_data['file_field']
        return data


class GlossVideoPosterForm(forms.ModelForm):
    class Meta:
        model = GlossVideo
        fields = ['posterfile', 'id']