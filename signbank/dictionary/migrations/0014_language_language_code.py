# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0013_auto_20160323_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='language_code',
            field=models.CharField(help_text=b"ISO 639-3 language code, set as 'und' if you don't have a code.", max_length=3, null=True, blank=True),
        ),
    ]
