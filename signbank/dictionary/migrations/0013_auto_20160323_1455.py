# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0012_auto_20160323_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='gloss',
            name='dataset',
            field=models.ForeignKey(default=1, to='dictionary.Dataset'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='gloss',
            unique_together=set([('idgloss', 'dataset')]),
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='language',
        ),
    ]
