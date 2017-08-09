# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def generate_signlanguage(apps, schema_editor):
    """
    Trying to generate a SignLanguage so that migrating is possible when app already has data.
    If the state of the app in the previous migration has a dataset, it is impossible to reference to SignLanguage,
    as the ForeignKey, because one does not exist. Here we try to create it, if objects.get does not find one.
    """
    SignLanguageModel = apps.get_model('dictionary', 'SignLanguage')
    try:
        SignLanguageModel.objects.get(id=1)
    except SignLanguageModel.DoesNotExist:
        SignLanguageModel.objects.create(id=1, name='TestSignLanguage', language_code_3char='tst')


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
        migrations.RunPython(generate_signlanguage, reverse_code=migrations.RunPython.noop),

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
            field=models.ManyToManyField(help_text='These languages are shown as optionsfor translation equivalents.', to='dictionary.Language'),
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
            field=models.BooleanField(default=False, help_text='Is this dataset is public or private?'),
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
