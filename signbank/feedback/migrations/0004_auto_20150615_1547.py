# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_auto_20150611_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signfeedback',
            name='translation',
            field=models.ForeignKey(blank=True, editable=False, to='dictionary.Translation', null=True),
        ),
    ]
