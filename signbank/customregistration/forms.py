from __future__ import unicode_literals

from registration.forms import RegistrationForm


class CustomUserForm(RegistrationForm):
    """Custom form to require users to add their first and last names when registering."""
    class Meta(RegistrationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
