# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_auto_20160828_1417'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signfeedback',
            name='translation_english',
        ),
    ]
