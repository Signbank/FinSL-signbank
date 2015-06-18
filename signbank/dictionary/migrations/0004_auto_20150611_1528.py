# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_auto_20150609_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_hki',
            field=models.CharField(help_text="\n    This is the Helsinki name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Helsinki Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", unique=True, max_length=30, verbose_name=b'Gloss: HKI', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_jkl',
            field=models.CharField(help_text="\n    This is the Jyvaskyla name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Jyvaskyla Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", unique=True, max_length=30, verbose_name=b'Gloss: JKL', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='domhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Strong Hand', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='final_domhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Final Dominant Handshape', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='final_subhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Final Subordinate Handshape', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='idgloss',
            field=models.CharField(help_text='\n    This is the unique identifying name of an entry of a sign form in the\ndatabase. No two Sign Entry Names can be exactly the same, but a "Sign\nEntry Name" can be (and often is) the same as the Annotation Idgloss.', unique=True, max_length=50, verbose_name=b'ID Gloss'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='subhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Weak Hand', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki')]),
        ),
    ]
