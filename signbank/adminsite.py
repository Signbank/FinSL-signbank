from __future__ import unicode_literals

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from signbank.contentpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

publisher_admin = AdminSite('flatpageadmin')
publisher_admin.register(FlatPage, FlatPageAdmin)
publisher_admin.register(User, UserAdmin)
