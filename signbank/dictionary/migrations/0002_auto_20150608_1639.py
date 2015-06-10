# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='annotation_idgloss_en',
        ),
        migrations.AddField(
            model_name='gloss',
            name='annotation_idgloss_hki',
            field=models.CharField(help_text=b"\n    This is the Helsinki name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Helsinki Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name=b'Gloss: HKI', blank=True),
        ),
        migrations.AddField(
            model_name='gloss',
            name='annotation_idgloss_hki_en',
            field=models.CharField(help_text=b'\n    This is the English name for the corresponding Jyvaskyla Gloss', max_length=30, verbose_name=b'Gloss: HKI (Eng)', blank=True),
        ),
        migrations.AddField(
            model_name='gloss',
            name='annotation_idgloss_jkl_en',
            field=models.CharField(help_text=b'\n    This is the English name for the corresponding Jyvaskyla Gloss', max_length=30, verbose_name=b'Gloss: JKL (Eng)', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_jkl',
            field=models.CharField(help_text=b"\n    This is the Jyvaskyla name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Jyvaskyla Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name=b'Gloss: JKL', blank=True),
        ),
    ]
