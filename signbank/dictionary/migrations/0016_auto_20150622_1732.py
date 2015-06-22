# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0015_auto_20150618_1044'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gloss',
            old_name='altern',
            new_name='alternating_movement',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='iconImg',
            new_name='iconic_image',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='mouthG',
            new_name='mouth_gesture',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='phonetVar',
            new_name='phonetic_variation',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='phonOth',
            new_name='phonology_other',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='repeat',
            new_name='repeated_movement',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='absOriFing',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='absOriPalm',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='contType',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='handCh',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='movDir',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='movMan',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='movSh',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='namEnt',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='oriCh',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='relOriLoc',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='relOriMov',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='relatArtic',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='semField',
        ),
        migrations.AddField(
            model_name='gloss',
            name='absolute_orientation_fingers',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Absolute Orientation: Fingers', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='absolute_orientation_palm',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Absolute Orientation: Palm', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='contact_type',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Contact Type', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='handshape_change',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Handshape Change', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='movement_direction',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Direction', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='movement_manner',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Manner', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='movement_shape',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Movement Shape', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='named_entity',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Named Entity', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='orientation_change',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Orientation Change', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='relation_between_articulators',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relation between Articulators', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='relative_orientation_location',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relative Orientation: Location', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='relative_orientation_movement',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Relative Orientation: Movement', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AddField(
            model_name='gloss',
            name='semantic_field',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Semantic Field', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='handedness',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Handedness', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='location',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Location', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='sense',
            field=models.IntegerField(help_text='If there is more than one sense of a sign enter a number here,\n                                       all signs with sense>1 will use the same video as sense=1', null=True, verbose_name='Sense Number', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='strong_handshape',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Strong Hand', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='weak_handshape',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Weak Hand', choices=[(b'0', b'-'), (b'1', b'N/A')]),
        ),
    ]
