# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0019_auto_20160902_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('language_code_3char', models.CharField(help_text='ISO 639-3 language code (3 characters long) of a sign language.', max_length=3)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='language',
        ),
        migrations.RemoveField(
            model_name='language',
            name='language_code',
        ),
        migrations.AddField(
            model_name='dataset',
            name='translation_languages',
            field=models.ManyToManyField(help_text=b'These languages are shown as optionsfor translation equivalents.', to='dictionary.Language'),
        ),
        migrations.AddField(
            model_name='language',
            name='language_code_2char',
            field=models.CharField(default='en', help_text='ISO 639-1 language code (2 characters long) of a written language.', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='language',
            name='language_code_3char',
            field=models.CharField(default='eng', help_text='ISO 639-3 language code (3 characters long) of a written language.', max_length=3),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dataset',
            name='is_public',
            field=models.BooleanField(default=False, help_text=b'Is this dataset is public or private?'),
        ),
        migrations.AlterField(
            model_name='dialect',
            name='language',
            field=models.ForeignKey(to='dictionary.SignLanguage'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='signlanguage',
            field=models.ForeignKey(default=1, to='dictionary.SignLanguage'),
            preserve_default=False,
        ),
    ]
