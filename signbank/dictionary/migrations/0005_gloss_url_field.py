# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_auto_20150811_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='gloss',
            name='url_field',
            field=models.URLField(verbose_name='URL', blank=True),
        ),
    ]
