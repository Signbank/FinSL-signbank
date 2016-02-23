# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_keywordenglish_translationenglish'),
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='signfeedback',
            name='translation_english',
            field=models.ForeignKey(blank=True, editable=False, to='dictionary.TranslationEnglish', null=True),
        ),
    ]
