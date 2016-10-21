# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0020_auto_20160913_1404'),
        ('video', '0002_auto_20161013_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='glossvideo',
            name='dataset',
            field=models.ForeignKey(to='dictionary.Dataset', null=True),
        ),
    ]
