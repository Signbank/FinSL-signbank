# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0013_remove_gloss_locvirtobj'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gloss',
            old_name='inWeb',
            new_name='in_web_dictionary',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='isNew',
            new_name='is_proposed_new_sign',
        ),
    ]
