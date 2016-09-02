# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0018_auto_20160902_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='language_code',
            field=models.CharField(help_text="ISO 639-3 language code, set as 'und' if you don't have a code. Please set this correctly to get translation\n        equivalents to work in search.", max_length=3),
        ),
        migrations.AlterUniqueTogether(
            name='translation',
            unique_together=set([('gloss', 'language', 'keyword')]),
        ),
    ]
