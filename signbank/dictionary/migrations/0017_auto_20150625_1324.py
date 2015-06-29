# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0016_auto_20150622_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gloss',
            name='absolute_orientation_fingers',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Absolute Orientation: Fingers', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'501', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='absolute_orientation_palm',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Absolute Orientation: Palm', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'401', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='contact_type',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Contact Type', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1301', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='handedness',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Handedness', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'101', 'Vaihtoehto1'), (b'102', 'Vaihtoehto2'), (b'103', 'Vaihtoehto3'), (b'104', 'Vaihtoehto4'), (b'105', 'Vaihtoehto5')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='handshape_change',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Handshape Change', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'901', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='location',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Location', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'301', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movement_direction',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Direction', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1101', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movement_manner',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Manner', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movement_shape',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Shape', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1001', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='named_entity',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Named Entity', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1401', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='orientation_change',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Orientation Change', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'10', 'Orientaatiomuutos yksi'), (b'801', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relation_between_articulators',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relation between Articulators', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'401', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relative_orientation_location',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relative Orientation: Location', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'701', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relative_orientation_movement',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relative Orientation: Movement', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'601', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='semantic_field',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Semantic Field', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'11', 'Semanttisuus'), (b'1501', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='strong_handshape',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Strong Hand', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki'), (b'201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='weak_handshape',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Weak Hand', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'1', 'K\xe4mmen'), (b'2', 'Nyrkki'), (b'201', 'Vaihtoehto1')]),
        ),
        migrations.AlterField(
            model_name='morphologydefinition',
            name='role',
            field=models.CharField(max_length=5, choices=[(b'0', b'-'), (b'1', b'N/A'), (b'2010', 'Yhdysviittoma'), (b'2011', 'Nominaali'), (b'2012', 'Verbaali-1'), (b'2013', 'Verbaali-2'), (b'2014', 'Verbaali-3'), (b'2015', 'Klassifikaattorik\xe4simuoto'), (b'2016', 'Numeraali k\xe4simuoto')]),
        ),
        migrations.AlterField(
            model_name='relation',
            name='role',
            field=models.CharField(max_length=20, choices=[(b'0', b'-'), (b'1', b'N/A'), (b'2010', 'Yhdysviittoma'), (b'2011', 'Nominaali'), (b'2012', 'Verbaali-1'), (b'2013', 'Verbaali-2'), (b'2014', 'Verbaali-3'), (b'2015', 'Klassifikaattorik\xe4simuoto'), (b'2016', 'Numeraali k\xe4simuoto')]),
        ),
    ]
