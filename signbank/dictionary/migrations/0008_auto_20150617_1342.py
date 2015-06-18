# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0007_auto_20150617_1243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='StemSN',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='compound',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='morph',
        ),
    ]
