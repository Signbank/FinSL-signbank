# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0008_auto_20151030_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gloss',
            name='annotation_comments',
            field=models.CharField(max_length=200, verbose_name='Comments', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_hki',
            field=models.CharField(help_text="\n    This is the Helsinki name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Helsinki Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=60, verbose_name='Gloss HKI', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_hki_en',
            field=models.CharField(help_text='\n    This is the English name for the corresponding Jyvaskyla Gloss', max_length=60, verbose_name='Gloss HKI (Eng)', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_jkl',
            field=models.CharField(help_text="\n    This is the Jyvaskyla name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Jyvaskyla Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=60, verbose_name='Gloss JKL', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_jkl_en',
            field=models.CharField(help_text='\n    This is the English name for the corresponding Jyvaskyla Gloss', max_length=60, verbose_name='Gloss JKL (Eng)', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='idgloss',
            field=models.CharField(help_text='\n    This is the unique identifying name of an entry of a sign form in the\ndatabase. No two Sign Entry Names can be exactly the same, but a "Sign\nEntry Name" can be (and often is) the same as the Annotation Idgloss.', max_length=60, verbose_name='Gloss'),
        ),
    ]
