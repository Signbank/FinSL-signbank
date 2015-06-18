# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_auto_20150611_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldchoice',
            name='field',
            field=models.CharField(max_length=50, choices=[(b'Handedness', b'Handedness'), (b'Handshape', b'Handshape'), (b'Location', b'Final Primary Location'), (b'RelatArtic', b'Relation between Articulators'), (b'AbsOriFing', b'Absolute Orientation: Fingers'), (b'RelOriMov', b'Relative Orientation: Movement'), (b'RelOriLoc', b'Relative Orientation: Location'), (b'OriChange', b'Orientation Change'), (b'HandshapeChange', b'Handshape Change'), (b'MovementShape', b'Movement Shape'), (b'MovementDir', b'Movement Direction'), (b'MovementMan', b'Movement Manner'), (b'ContactType', b'Contact Type'), (b'NamedEntity', b'Named Entity'), (b'SemField', b'Semantic Field')]),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='oriCh',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Orientation Change', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'10', 'Orientaatiomuutos yksi')]),
        ),
    ]
