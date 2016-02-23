# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0007_auto_20151016_1346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='sense',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='sn',
        ),
    ]
