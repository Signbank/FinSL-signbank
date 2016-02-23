# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='auslan_user',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='australian',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='background',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='deaf',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='learned',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='postcode',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='school',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='schooltype',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='teachercomm',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='yob',
        ),
    ]
