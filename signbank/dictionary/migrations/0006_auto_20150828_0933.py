# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0005_gloss_url_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gloss',
            name='annotation_comments',
            field=models.CharField(max_length=50, verbose_name='Comments', blank=True),
        ),
    ]
