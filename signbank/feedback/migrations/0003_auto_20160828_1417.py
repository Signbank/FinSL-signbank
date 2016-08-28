# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_signfeedback_translation_english'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signfeedback',
            name='correct',
        ),
        migrations.RemoveField(
            model_name='signfeedback',
            name='isAuslan',
        ),
        migrations.RemoveField(
            model_name='signfeedback',
            name='like',
        ),
        migrations.RemoveField(
            model_name='signfeedback',
            name='suggested',
        ),
        migrations.RemoveField(
            model_name='signfeedback',
            name='use',
        ),
        migrations.RemoveField(
            model_name='signfeedback',
            name='whereused',
        ),
    ]
