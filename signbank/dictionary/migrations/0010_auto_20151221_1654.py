# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0009_auto_20151106_1019'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gloss',
            options={'ordering': ['idgloss'], 'verbose_name_plural': 'Glosses', 'permissions': (('update_video', 'Can Update Video'), ('search_gloss', 'Can Search/View Full Gloss Details'), ('export_csv', 'Can export sign details as CSV'), ('can_publish', 'Can publish signs and definitions'), ('can_delete_unpublished', 'Can delete unpub signs or defs'), ('can_delete_published', 'Can delete pub signs and defs'), ('view_advanced_properties', 'Include all properties in sign detail view'), ('lock_gloss', 'Can lock and unlock Gloss from editing'))},
        ),
        migrations.AddField(
            model_name='gloss',
            name='locked',
            field=models.BooleanField(default=False, verbose_name='Locked'),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='dialect',
            field=models.ManyToManyField(to='dictionary.Dialect', blank=True),
        ),
        migrations.AlterField(
            model_name='gloss',
            name='language',
            field=models.ManyToManyField(to='dictionary.Language', blank=True),
        ),
    ]
