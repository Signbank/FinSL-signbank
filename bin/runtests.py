#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "signbank.settings.testing")

    from django import setup
    from django.conf import settings
    from django.core.management import call_command

    apps_for_testing = [app for app in settings.INSTALLED_APPS
                        if app.startswith("signbank.")]

    setup()
    call_command("test", *apps_for_testing)
