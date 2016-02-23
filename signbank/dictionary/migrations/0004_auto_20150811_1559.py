# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_keywordenglish_translationenglish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialect',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
