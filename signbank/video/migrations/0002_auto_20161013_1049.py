# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='glossvideo',
            name='gloss',
            field=models.ForeignKey(to='dictionary.Gloss', null=True),
        ),
    ]
