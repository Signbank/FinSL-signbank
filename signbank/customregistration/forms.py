# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormTermsOfService


class CustomUserForm(RegistrationFormTermsOfService):
    """Custom form to require users to add their first and last names when registering,
    and to allow translation of tos."""
    class Meta(RegistrationFormTermsOfService.Meta):
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'tos']

    def __init__(self, *args, **kwargs):
        super(RegistrationFormTermsOfService, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['tos'].label = _('I have read and agree to the Terms of Service')
