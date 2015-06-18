# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0011_remove_gloss_inittext'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='final_palm_orientation',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='final_relative_orientation',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='initial_palm_orientation',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='initial_relative_orientation',
        ),
    ]
