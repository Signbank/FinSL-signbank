# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from registration.forms import RegistrationForm, RegistrationFormTermsOfService


class CustomUserForm(RegistrationFormTermsOfService):
    """Custom form to require users to add their first and last names when registering."""
    class Meta(RegistrationFormTermsOfService.Meta):
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'tos']

    def __init__(self, *args, **kwargs):
        super(RegistrationFormTermsOfService, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
