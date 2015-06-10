# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_auto_20150608_1639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='aslgloss',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='asloantf',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='asltf',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='blend',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='blendtf',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='bslgloss',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='bslloantf',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='bsltf',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='sedefinetf',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='segloss',
        ),
    ]
