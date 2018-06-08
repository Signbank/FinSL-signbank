from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from registration.signals import user_registered
from notifications.signals import notify


@receiver(user_registered)
def notify_on_account_creation(sender, **kwargs):
    """When a user creates an account, send a notification to Users in 'Super admin' group (with is_staff=True)."""
    acc = kwargs["user"]
    notify.send(sender=acc, recipient=User.objects.filter(is_staff=True, is_superuser=True),
                verb=_("created an account."), public=False,
                description="{acc.first_name} {acc.last_name} {created}: '{acc}'. {emailtxt}: {acc.email}".format(
                    acc=acc, created=_("created an account"), emailtxt=_("Email")),
                )