# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_auto_20150610_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='content_en',
            field=models.TextField(null=True, verbose_name='content', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='content_fi',
            field=models.TextField(null=True, verbose_name='content', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='title_en',
            field=models.CharField(max_length=200, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='page',
            name='title_fi',
            field=models.CharField(max_length=200, null=True, verbose_name='title'),
        ),
    ]
