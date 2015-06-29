# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='group_required',
            field=models.ManyToManyField(help_text='This page will only be visible to members of these groups, leave blank to allow anyone to access.', to='auth.Group', blank=True),
        ),
    ]
