# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import GlossVideo
from signbank.dictionary.models import Dataset, Gloss


class VideoUploadForm(forms.ModelForm):
    """Form for video upload"""

    class Meta:
        model = GlossVideo
        exclude = ()


class VideoUploadAddGlossForm(forms.Form):
    """Form for video upload for a particular gloss"""
    # Translators: VideoUploadForGlossForm
    videofile = forms.FileField(label=_("Upload Video"))
    video_title = forms.CharField(label=_('Glossvideo title'), required=False)


class VideoUploadForGlossForm(forms.Form):
    """Form for video upload for a particular gloss"""
    # Translators: VideoUploadForGlossForm
    videofile = forms.FileField(label=_("Upload Video"))
    video_title = forms.CharField(label=_('Glossvideo title'), required=False)
    gloss_id = forms.CharField(widget=forms.HiddenInput)
    redirect = forms.CharField(widget=forms.HiddenInput, required=False)


class MultipleVideoUploadForm(forms.Form):
    """Form for uploading multiple videos."""
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'onchange': 'updateSize();'}))
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all(), required=True, empty_label=None)

    def clean_file_field(self):
        data = self.cleaned_data['file_field']
        return data


class UpdateGlossVideoForm(forms.ModelForm):

    gloss = forms.ModelChoiceField(queryset=Gloss.objects.all(), widget=forms.TextInput)

    class Meta:
        model = GlossVideo
        fields = ['dataset', 'videofile', 'gloss']


class PosterUpload(forms.ModelForm):
    class Meta:
        model = GlossVideo
        fields = ['posterfile', 'id']