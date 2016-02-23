# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0010_auto_20151221_1654'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='annotation_idgloss_hki',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='annotation_idgloss_hki_en',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='annotation_idgloss_jkl',
        ),
       	migrations.RenameField(
            model_name='gloss',
            old_name='annotation_idgloss_jkl_en',
       	    new_name='idgloss_en',
        ),
       	migrations.AlterField(
            model_name='gloss',
            name='idgloss_en',
            field=models.CharField(help_text='This is the English name for the Gloss', max_length=60, verbose_name='Gloss in English', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='idgloss',
            field=models.CharField(help_text='This is the unique identifying name of a Gloss.', max_length=60, verbose_name='Gloss'),
        ),
    ]
