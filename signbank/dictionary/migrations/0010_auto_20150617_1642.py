# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0009_remove_gloss_comptf'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gloss',
            old_name='annotationComments',
            new_name='annotation_comments',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='locprim',
            new_name='location',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='domhndsh',
            new_name='strong_handshape',
        ),
        migrations.RenameField(
            model_name='gloss',
            old_name='subhndsh',
            new_name='weak_handshape',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='final_domhndsh',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='final_loc',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='final_secondary_loc',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='final_subhndsh',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='initial_secondary_loc',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='locsecond',
        ),
    ]
