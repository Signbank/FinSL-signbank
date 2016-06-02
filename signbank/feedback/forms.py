from django import forms
from django.utils.translation import ugettext_lazy as _

from signbank.video.fields import VideoUploadToFLVField
from signbank.feedback.models import *

__author__ = 'heilniem'


class InterpreterFeedbackForm(forms.ModelForm):
    class Meta:
        model = InterpreterFeedback
        fields = ['comment']
        widgets = {'comment': forms.Textarea(attrs={'cols': 30, 'rows': 2})}


class GeneralFeedbackForm(forms.Form):
    """Form for general feedback"""

    comment = forms.CharField(
        widget=forms.Textarea(attrs={'cols': '64'}), required=False)
    video = VideoUploadToFLVField(
        required=False, widget=forms.FileInput(attrs={'size': '60'}))


class SignFeedbackForm(forms.Form):
    """Form for input of sign feedback"""

    # correct = forms.IntegerField(initial=0, widget=forms.HiddenInput)
    kwnotbelong = forms.CharField(
        # Translators: keywordnotbelong, label name
        label=_("List keywords"), required=False, widget=forms.Textarea)
    comment = forms.CharField(required=False, widget=forms.Textarea)


class MissingSignFeedbackForm(forms.Form):
    # Translators: Missing sign feedback (handform)
    handform = forms.ChoiceField(choices=handformChoices, required=False,
                                 label=_('How many hands are used to make this sign?'))
    # Translators: Missing sign feedback (handshape)
    handshape = forms.ChoiceField(choices=handshapeChoices, required=False,
                                  label=_('What is the handshape?'))
    # Translators: Missing sign feedback (althandshape)
    althandshape = forms.ChoiceField(choices=handshapeChoices, required=False,
                                     label=_('What is the handshape of the left hand?'))
    # Translators: Missing sign feedback (location)
    location = forms.ChoiceField(choices=locationChoices, required=False,
                                 label=_('Choose the location of the sign on, or near the body'))
    # Translators: Missing sign feedback (relativelocation)
    relativelocation = forms.ChoiceField(choices=relativelocationChoices,
                                         label=_('Choose the location of the right hand on, or near the left hand'),
                                         required=False)
    # Translators: Missing sign feedback (handbodycontact)
    handbodycontact = forms.ChoiceField(choices=handbodycontactChoices,
                                        label=_('Contact between hands and body'), required=False)
    # Translators: Missing sign feedback (handinteraction)
    handinteraction = forms.ChoiceField(choices=handinteractionChoices,
                                        label=_('Interaction between hands'), required=False)
    # Translators: Missing sign feedback (direction)
    direction = forms.ChoiceField(choices=directionChoices,
                                  label=_('Movement direction of the hand(s)'), required=False)
    # Translators: Missing sign feedback (movementtype)
    movementtype = forms.ChoiceField(choices=movementtypeChoices,
                                     label=_('Type of movement'), required=False)
    # Translators: Missing sign feedback (smallmovement)
    smallmovement = forms.ChoiceField(choices=smallmovementChoices,
                                      label=_('Small movements of the hand(s) and fingers'), required=False)
    # Translators: Missing sign feedback (repetition)
    repetition = forms.ChoiceField(choices=repetitionChoices,
                                   label=_('Number of movements'), required=False)
    # Translators: Missing sign feedback (meaning)
    meaning = forms.CharField(label=_('Sign Meaning'),
                              widget=forms.Textarea(attrs={'cols': '55', 'rows': '8'}))
    video = forms.FileField(required=False,
                            widget=forms.FileInput(attrs={'size': '60'}))
    # Translators: Missing sign feedback (comments)
    comments = forms.CharField(label=_('Further Details'),
                               widget=forms.Textarea(attrs={'cols': '55', 'rows': '8'}), required=False)
