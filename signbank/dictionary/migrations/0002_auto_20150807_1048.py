# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gloss',
            name='absolute_orientation_fingers',
            field=models.ForeignKey(related_name='absolute_orientation_fingers', db_column=b'absolute_orientation_fingers', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Absolute Orientation: Fingers'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='absolute_orientation_palm',
            field=models.ForeignKey(related_name='absolute_orientation_palm', db_column=b'absolute_orientation_palm', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Absolute Orientation: Palm'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='contact_type',
            field=models.ForeignKey(related_name='contact_type', db_column=b'contact_type', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Contact Type'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='handedness',
            field=models.ForeignKey(related_name='handedness', db_column=b'handedness', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Handedness'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='handshape_change',
            field=models.ForeignKey(related_name='handshape_change', db_column=b'handshape_change', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Handshape Change'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='location',
            field=models.ForeignKey(related_name='location', db_column=b'location', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movement_direction',
            field=models.ForeignKey(related_name='movement_direction', db_column=b'movement_direction', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Movement Direction'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movement_manner',
            field=models.ForeignKey(related_name='movement_manner', db_column=b'movement_manner', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Movement Manner'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='movement_shape',
            field=models.ForeignKey(related_name='movement_shape', db_column=b'movement_shape', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Movement Shape'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='named_entity',
            field=models.ForeignKey(related_name='named_entity', db_column=b'named_entity', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Named Entity'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='orientation_change',
            field=models.ForeignKey(related_name='orientation_change', db_column=b'orientation_change', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Orientation Change'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relation_between_articulators',
            field=models.ForeignKey(related_name='relation_between_articulators', db_column=b'relation_between_articulators', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Relation Between Articulators'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relative_orientation_location',
            field=models.ForeignKey(related_name='relative_orientation_location', db_column=b'relative_orientation_location', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Relative Orientation: Location'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='relative_orientation_movement',
            field=models.ForeignKey(related_name='relative_orientation_movement', db_column=b'relative_orientation_movement', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Relative Orientation: Movement'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='semantic_field',
            field=models.ForeignKey(related_name='semantic_field', db_column=b'semantic_field', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Semantic Field'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='strong_handshape',
            field=models.ForeignKey(related_name='strong_handshape', db_column=b'strong_handshape', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Strong Hand'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='weak_handshape',
            field=models.ForeignKey(related_name='weak_handshape', db_column=b'weak_handshape', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice', null=True, verbose_name='Weak Hand'),
        ),
        migrations.AlterField(
            model_name='morphologydefinition',
            name='role',
            field=models.ForeignKey(db_column=b'MorphologyType', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice'),
        ),
        migrations.AlterField(
            model_name='relation',
            name='role',
            field=models.ForeignKey(db_column=b'MorphologyType', to_field=b'machine_value', blank=True, to='dictionary.FieldChoice'),
        ),
    ]
