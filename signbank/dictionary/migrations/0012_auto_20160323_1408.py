# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0011_auto_20160205_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60)),
                ('is_public', models.BooleanField(default=False, help_text='Tells whether this dataset is public or private')),
                ('description', models.TextField()),
                ('language', models.ForeignKey(to='dictionary.Language')),
            ],
        ),
    ]
