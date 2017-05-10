# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0017_auto_20160828_1417'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='translationenglish',
            name='gloss',
        ),
        migrations.RemoveField(
            model_name='translationenglish',
            name='translation_english',
        ),
        migrations.RenameField(
            model_name='translation',
            old_name='translation',
            new_name='keyword',
        ),
        migrations.AddField(
            model_name='translation',
            name='language',
            field=models.ForeignKey(default=1, to='dictionary.Language'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='KeywordEnglish',
        ),
        migrations.DeleteModel(
            name='TranslationEnglish',
        ),
    ]
