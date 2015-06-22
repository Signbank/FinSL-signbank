# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0014_auto_20150618_0940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='tokNo',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoA',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoGe',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoGr',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoO',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoR',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoSgnr',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoSgnrA',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoSgnrGe',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoSgnrGr',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoSgnrO',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoSgnrR',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoSgnrV',
        ),
        migrations.RemoveField(
            model_name='gloss',
            name='tokNoV',
        ),
        migrations.AddField(
            model_name='gloss',
            name='number_of_occurences',
            field=models.IntegerField(help_text=b'Number of occurences in annotation materials', null=True, verbose_name='Number of Occurrences', blank=True),
        ),
    ]
