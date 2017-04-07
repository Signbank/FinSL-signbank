from django import forms
from django.utils.translation import ugettext_lazy as _

from models import GlossVideo
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


class GlossVideoAdminForm(forms.ModelForm):
    gloss = forms.ModelChoiceField(queryset=Gloss.objects.all(), required=False)
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(GlossVideoAdminForm, self).__init__(*args, **kwargs)
        # Set posterfile field to be not required.
        self.fields['posterfile'].required = False
        # If GlossVideo has no Dataset, try to get it from gloss.dataset.
        if hasattr(self.instance, 'dataset') and not self.instance.dataset:
            try:
                self.instance.dataset = self.instance.gloss.dataset
                self.instance.save()
            except AttributeError:
                pass
        # Try to use glossvideos dataset as a filter for glosses.
        # (If glossvideo did not have a dataset but its gloss had, glossvideo should have gloss.dataset as its dataset).
        try:
            self.fields['gloss'].queryset = Gloss.objects.filter(
                dataset=self.instance.dataset)
        except AttributeError:
            pass


class UpdateGlossVideoForm(forms.ModelForm):
    class Meta:
        model = GlossVideo
        fields = ['dataset', 'videofile', 'gloss']


class PosterUpload(forms.ModelForm):
    class Meta:
        model = GlossVideo
        fields = ['posterfile', 'id']