# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import GlossVideo
from signbank.dictionary.models import Dataset, Gloss


class GlossVideoForm(forms.ModelForm):
    """Form for GlossVideo."""
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