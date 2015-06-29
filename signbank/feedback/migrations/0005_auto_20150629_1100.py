# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0004_auto_20150615_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signfeedback',
            name='isAuslan',
            field=models.IntegerField(verbose_name='Is this sign an FinSL Sign?', choices=[(1, 'yes'), (2, 'Perhaps'), (3, "Don't know"), (4, "Don't think so"), (5, 'No'), (0, 'N/A')]),
        ),
    ]
