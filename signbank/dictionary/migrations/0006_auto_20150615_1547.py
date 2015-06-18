# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0005_auto_20150611_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldchoice',
            name='field',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='absOriFing',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Absolute Orientation: Fingers', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'501', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='absOriPalm',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Absolute Orientation: Palm', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'401', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_hki',
            field=models.CharField(help_text="\n    This is the Helsinki name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Helsinki Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name=b'Gloss: HKI', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='annotation_idgloss_jkl',
            field=models.CharField(help_text="\n    This is the Jyvaskyla name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Jyvaskyla Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name=b'Gloss: JKL', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='contType',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Contact Type', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1301', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='domhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Strong Hand', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki'), (b'201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='final_domhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Final Dominant Handshape', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki'), (b'201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='final_loc',
            field=models.IntegerField(blank=True, null=True, verbose_name='Final Primary Location', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'301', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='final_subhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Final Subordinate Handshape', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki'), (b'201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='handCh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Handshape Change', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'901', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='handedness',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Handedness', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'101', 'Vaihtoehto1'), (b'102', 'Vaihtoehto2'), (b'103', 'Vaihtoehto3'), (b'104', 'Vaihtoehto4'), (b'105', 'Vaihtoehto5')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='idgloss',
            field=models.CharField(help_text='\n    This is the unique identifying name of an entry of a sign form in the\ndatabase. No two Sign Entry Names can be exactly the same, but a "Sign\nEntry Name" can be (and often is) the same as the Annotation Idgloss.', max_length=50, verbose_name='ID Gloss'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='locsecond',
            field=models.IntegerField(blank=True, null=True, verbose_name='Secondary Location', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'301', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movDir',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Direction', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1101', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movMan',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Manner', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movSh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Shape', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1001', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='namEnt',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Named Entity', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1401', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='oriCh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Orientation Change', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'10', 'Orientaatiomuutos yksi'), (b'801', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relOriLoc',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relative Orientation: Location', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'701', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relOriMov',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relative Orientation: Movement', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'601', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relatArtic',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relation between Articulators', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'401', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='semField',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Semantic Field', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'11', 'Semanttisuus'), (b'1501', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='subhndsh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Weak Hand', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki'), (b'201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='relation',
            name='role',
            field=models.CharField(max_length=20, choices=[(b'0', b'-'), (b'1', b'N/A'), (b'2010', 'Kaari')]),
        ),
    ]
