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
    webcam = forms.BooleanField(required=False)

    class Meta:
        model = GlossVideo
        fields = ["title", "videofile", "gloss"]


class GlossVideoUpdateForm(forms.ModelForm):
    """Form for adding Gloss and Dataset to GlossVideo."""
    gloss = forms.ModelChoiceField(queryset=Gloss.objects.none(), widget=forms.TextInput)

    class Meta:
        model = GlossVideo
        fields = ['dataset', 'videofile', 'gloss']




class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    attrs={'multiple': True, 'onchange': 'updateSize();'}

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class MultipleVideoUploadForm(forms.Form):
    """Form for uploading multiple videos."""
    allow_multiple_selected = True
    file_field = MultipleFileField()
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all(), required=True, empty_label=None)

    def clean_file_field(self):
        data = self.cleaned_data['file_field']
        return data


class GlossVideoPosterForm(forms.ModelForm):
    class Meta:
        model = GlossVideo
        fields = ['posterfile', 'id']