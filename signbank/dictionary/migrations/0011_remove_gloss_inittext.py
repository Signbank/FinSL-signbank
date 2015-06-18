# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0010_auto_20150617_1642'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='inittext',
        ),
    ]
