# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('role', models.CharField(max_length=20, verbose_name='Type', choices=[('note', 'Note'), ('privatenote', 'Private Note'), ('phon', 'Phonology'), ('todo', 'To Do'), ('sugg', 'Suggestion for other gloss')])),
                ('count', models.IntegerField()),
                ('published', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['gloss', 'role', 'count'],
            },
        ),
        migrations.CreateModel(
            name='Dialect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ['language', 'name'],
            },
        ),
        migrations.CreateModel(
            name='FieldChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(max_length=50)),
                ('english_name', models.CharField(max_length=50)),
                ('machine_value', models.IntegerField(unique=True)),
            ],
            options={
                'ordering': ['field', 'machine_value'],
            },
        ),
        migrations.CreateModel(
            name='Gloss',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('idgloss', models.CharField(help_text='\n    This is the unique identifying name of an entry of a sign form in the\ndatabase. No two Sign Entry Names can be exactly the same, but a "Sign\nEntry Name" can be (and often is) the same as the Annotation Idgloss.', max_length=50, verbose_name='Gloss')),
                ('annotation_idgloss_jkl', models.CharField(help_text="\n    This is the Jyvaskyla name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Jyvaskyla Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name='Gloss JKL', blank=True)),
                ('annotation_idgloss_jkl_en', models.CharField(help_text='\n    This is the English name for the corresponding Jyvaskyla Gloss', max_length=30, verbose_name='Gloss JKL (Eng)', blank=True)),
                ('annotation_idgloss_hki', models.CharField(help_text="\n    This is the Helsinki name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Helsinki Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name='Gloss HKI', blank=True)),
                ('annotation_idgloss_hki_en', models.CharField(help_text='\n    This is the English name for the corresponding Jyvaskyla Gloss', max_length=30, verbose_name='Gloss HKI (Eng)', blank=True)),
                ('annotation_comments', models.CharField(max_length=50, verbose_name='Annotation comments', blank=True)),
                ('sense', models.IntegerField(help_text='If there is more than one sense of a sign enter a number here,\n                                       all signs with sense>1 will use the same video as sense=1', null=True, verbose_name='Sense Number', blank=True)),
                ('sn', models.IntegerField(help_text='Sign Number must be a unique integer and defines the ordering of signs in the dictionary', unique=True, null=True, verbose_name='Sign Number', blank=True)),
                ('repeated_movement', models.NullBooleanField(default=False, verbose_name='Repeated Movement')),
                ('alternating_movement', models.NullBooleanField(default=False, verbose_name='Alternating Movement')),
                ('phonology_other', models.TextField(null=True, verbose_name='Phonology Other', blank=True)),
                ('mouth_gesture', models.CharField(max_length=50, verbose_name='Mouth Gesture', blank=True)),
                ('mouthing', models.CharField(max_length=50, verbose_name='Mouthing', blank=True)),
                ('phonetic_variation', models.CharField(max_length=50, verbose_name='Phonetic Variation', blank=True)),
                ('iconic_image', models.CharField(max_length=50, verbose_name='Iconic Image', blank=True)),
                ('number_of_occurences', models.IntegerField(help_text='Number of occurences in annotation materials', null=True, verbose_name='Number of Occurrences', blank=True)),
                ('in_web_dictionary', models.NullBooleanField(default=False, verbose_name='In the Web dictionary')),
                ('is_proposed_new_sign', models.NullBooleanField(default=False, verbose_name='Is this a proposed new sign?')),
                ('absolute_orientation_fingers', models.ForeignKey(related_name='absolute_orientation_fingers', db_column='absolute_orientation_fingers', to_field='machine_value', to='dictionary.FieldChoice')),
                ('absolute_orientation_palm', models.ForeignKey(related_name='absolute_orientation_palm', db_column='absolute_orientation_palm', to_field='machine_value', to='dictionary.FieldChoice')),
                ('contact_type', models.ForeignKey(related_name='contact_type', db_column='contact_type', to_field='machine_value', to='dictionary.FieldChoice')),
                ('dialect', models.ManyToManyField(to='dictionary.Dialect')),
                ('handedness', models.ForeignKey(related_name='handedness', db_column='handedness', to_field='machine_value', to='dictionary.FieldChoice')),
                ('handshape_change', models.ForeignKey(related_name='handshape_change', db_column='handshape_change', to_field='machine_value', to='dictionary.FieldChoice')),
            ],
            options={
                'ordering': ['idgloss'],
                'verbose_name_plural': 'Glosses',
                'permissions': (('update_video', 'Can Update Video'), ('search_gloss', 'Can Search/View Full Gloss Details'), ('export_csv', 'Can export sign details as CSV'), ('can_publish', 'Can publish signs and definitions'), ('can_delete_unpublished', 'Can delete unpub signs or defs'), ('can_delete_published', 'Can delete pub signs and defs'), ('view_advanced_properties', 'Include all properties in sign detail view')),
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'ordering': ['text'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MorphologyDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('morpheme', models.ForeignKey(related_name='morphemes', to='dictionary.Gloss')),
                ('parent_gloss', models.ForeignKey(related_name='parent_glosses', to='dictionary.Gloss')),
                ('role', models.ForeignKey(to='dictionary.FieldChoice', db_column='MorphologyType', to_field='machine_value')),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.ForeignKey(to='dictionary.FieldChoice', db_column='MorphologyType', to_field='machine_value')),
                ('source', models.ForeignKey(related_name='relation_sources', to='dictionary.Gloss')),
                ('target', models.ForeignKey(related_name='relation_targets', to='dictionary.Gloss')),
            ],
            options={
                'ordering': ['source'],
            },
        ),
        migrations.CreateModel(
            name='RelationToForeignSign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('loan', models.BooleanField(default=False, verbose_name='Loan Sign')),
                ('other_lang', models.CharField(max_length=20, verbose_name='Related Language')),
                ('other_lang_gloss', models.CharField(max_length=50, verbose_name='Gloss in related language')),
                ('gloss', models.ForeignKey(to='dictionary.Gloss')),
            ],
            options={
                'ordering': ['gloss', 'loan', 'other_lang', 'other_lang_gloss'],
            },
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField(verbose_name='Index')),
                ('gloss', models.ForeignKey(to='dictionary.Gloss')),
                ('translation', models.ForeignKey(to='dictionary.Keyword')),
            ],
            options={
                'ordering': ['gloss', 'index'],
            },
        ),
        migrations.AddField(
            model_name='gloss',
            name='language',
            field=models.ManyToManyField(to='dictionary.Language'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='location',
            field=models.ForeignKey(related_name='location', db_column='location', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='movement_direction',
            field=models.ForeignKey(related_name='movement_direction', db_column='movement_direction', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='movement_manner',
            field=models.ForeignKey(related_name='movement_manner', db_column='movement_manner', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='movement_shape',
            field=models.ForeignKey(related_name='movement_shape', db_column='movement_shape', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='named_entity',
            field=models.ForeignKey(related_name='named_entity', db_column='named_entity', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='orientation_change',
            field=models.ForeignKey(related_name='orientation_change', db_column='orientation_change', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='relation_between_articulators',
            field=models.ForeignKey(related_name='relation_between_articulators', db_column='relation_between_articulators', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='relative_orientation_location',
            field=models.ForeignKey(related_name='relative_orientation_location', db_column='relative_orientation_location', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='relative_orientation_movement',
            field=models.ForeignKey(related_name='relative_orientation_movement', db_column='relative_orientation_movement', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='semantic_field',
            field=models.ForeignKey(related_name='semantic_field', db_column='semantic_field', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='strong_handshape',
            field=models.ForeignKey(related_name='strong_handshape', db_column='strong_handshape', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='weak_handshape',
            field=models.ForeignKey(related_name='weak_handshape', db_column='weak_handshape', to_field='machine_value', to='dictionary.FieldChoice'),
        ),
        migrations.AddField(
            model_name='dialect',
            name='language',
            field=models.ForeignKey(to='dictionary.Language'),
        ),
        migrations.AddField(
            model_name='definition',
            name='gloss',
            field=models.ForeignKey(to='dictionary.Gloss'),
        ),
    ]
