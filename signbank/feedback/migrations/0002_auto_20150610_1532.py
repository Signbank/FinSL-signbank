# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signfeedback',
            name='correct',
            field=models.IntegerField(verbose_name='Is the information about the sign correct?', choices=[(1, 'yes'), (2, 'Mostly Correct'), (3, 'En tied\xe4'), (4, 'Mostly Wrong'), (5, 'Ei'), (0, 'N/A')]),
        ),
        migrations.AlterField(
            model_name='signfeedback',
            name='like',
            field=models.IntegerField(verbose_name='Do you like this sign?', choices=[(1, 'yes'), (2, 'V\xe4h\xe4n'), (3, "Don't care"), (4, 'Ei paljon'), (5, 'Ei'), (0, 'N/A')]),
        ),
        migrations.AlterField(
            model_name='signfeedback',
            name='suggested',
            field=models.IntegerField(default=3, verbose_name='If this sign is a suggested new sign, would you use it?', choices=[(1, 'yes'), (2, 'Joskus'), (3, 'En tied\xe4'), (4, 'Perhaps'), (5, 'Ei'), (0, 'N/A')]),
        ),
        migrations.AlterField(
            model_name='signfeedback',
            name='use',
            field=models.IntegerField(verbose_name='Do you use this sign?', choices=[(1, 'yes'), (2, 'Joskus'), (3, 'Harvoin'), (4, 'Ei'), (0, 'N/A')]),
        ),
    ]
