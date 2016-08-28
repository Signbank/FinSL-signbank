# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0016_auto_20160517_1552'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gloss',
            options={'ordering': ['idgloss'], 'verbose_name_plural': 'Glosses', 'permissions': (('update_video', 'Can Update Video'), ('search_gloss', 'Can Search/View Full Gloss Details'), ('export_csv', 'Can export sign details as CSV'), ('can_publish', 'Can publish signs and definitions'), ('can_delete_unpublished', 'Can delete unpub signs or defs'), ('can_delete_published', 'Can delete pub signs and defs'), ('view_advanced_properties', 'Include all properties in sign detail view'), ('lock_gloss', 'Can lock and unlock Gloss from editing'), ('import_csv', 'Can import glosses from a CSV file'))},
        ),
    ]
