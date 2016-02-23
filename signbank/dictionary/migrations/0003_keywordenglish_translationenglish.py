# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_auto_20150807_1048'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeywordEnglish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'ordering': ['text'],
            },
        ),
        migrations.CreateModel(
            name='TranslationEnglish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField(verbose_name=b'Index')),
                ('gloss', models.ForeignKey(to='dictionary.Gloss')),
                ('translation_english', models.ForeignKey(to='dictionary.KeywordEnglish')),
            ],
            options={
                'ordering': ['gloss', 'index'],
            },
        ),
    ]
