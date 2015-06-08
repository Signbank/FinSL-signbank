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
                ('role', models.CharField(max_length=20, verbose_name=b'Type', choices=[(b'note', b'Note'), (b'privatenote', b'Private Note'), (b'phon', b'Phonology'), (b'todo', b'To Do'), (b'sugg', b'Suggestion for other gloss')])),
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
                ('machine_value', models.IntegerField()),
            ],
            options={
                'ordering': ['field', 'machine_value'],
            },
        ),
        migrations.CreateModel(
            name='Gloss',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('idgloss', models.CharField(help_text=b'\n    This is the unique identifying name of an entry of a sign form in the\ndatabase. No two Sign Entry Names can be exactly the same, but a "Sign\nEntry Name" can be (and often is) the same as the Annotation Idgloss.', max_length=50, verbose_name=b'ID Gloss')),
                ('annotation_idgloss_jkl', models.CharField(help_text=b"\n    This is the Dutch name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name=b'Gloss: JKL', blank=True)),
                ('annotation_idgloss_en', models.CharField(help_text=b"\n    This is the English name of a sign used by annotators when glossing the corpus in\nan ELAN annotation file. The Annotation Idgloss may be the same for two or\nmore entries (each with their own 'Sign Entry Name'). If two sign entries\nhave the same 'Annotation Idgloss' that means they differ in form in only\nminor or insignificant ways that can be ignored.", max_length=30, verbose_name=b'Gloss: HKI', blank=True)),
                ('bsltf', models.NullBooleanField(verbose_name=b'BSL sign')),
                ('asltf', models.NullBooleanField(verbose_name=b'ASL sign')),
                ('aslgloss', models.CharField(max_length=50, verbose_name=b'ASL gloss', blank=True)),
                ('asloantf', models.NullBooleanField(verbose_name=b'ASL loan sign')),
                ('bslgloss', models.CharField(max_length=50, verbose_name=b'BSL gloss', blank=True)),
                ('bslloantf', models.NullBooleanField(verbose_name=b'BSL loan sign')),
                ('useInstr', models.CharField(max_length=50, verbose_name=b'Annotation instructions', blank=True)),
                ('rmrks', models.CharField(max_length=50, verbose_name=b'Remarks', blank=True)),
                ('blend', models.CharField(max_length=100, null=True, verbose_name=b'Blend of', blank=True)),
                ('blendtf', models.NullBooleanField(verbose_name=b'Blend')),
                ('compound', models.CharField(max_length=100, verbose_name=b'Compound of', blank=True)),
                ('comptf', models.NullBooleanField(verbose_name=b'Compound')),
                ('handedness', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Handedness', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'75', 'My choice')])),
                ('domhndsh', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Strong Hand', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('subhndsh', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Weak Hand', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('final_domhndsh', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Final Dominant Handshape', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('final_subhndsh', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Final Subordinate Handshape', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('locprim', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'Location', choices=[(b'0', b'No Value Set'), (b'1', b'N/A'), (b'2', b'Neutral space > head'), (b'3', b'Neutral space'), (b'4', b'Shoulder'), (b'5', b'Weak hand'), (b'6', b'Weak hand > arm'), (b'7', b'Forehead'), (b'8', b'Chest'), (b'9', b'Neck'), (b'10', b'Head'), (b'11', b'Weak hand: back'), (b'12', b'Chin'), (b'13', b'Ring finger'), (b'14', b'Forehead, belly'), (b'15', b'Eye'), (b'16', b'Cheekbone'), (b'17', b'Face'), (b'18', b'Ear'), (b'19', b'Mouth'), (b'20', b'Low in neutral space'), (b'21', b'Arm'), (b'22', b'Nose'), (b'23', b'Cheek'), (b'24', b'Heup'), (b'25', b'Body'), (b'26', b'Belly'), (b'27', b'Tongue'), (b'28', b'Chin > neutral space'), (b'29', b'Locative'), (b'30', b'Head ipsi'), (b'31', b'Forehead > chin'), (b'32', b'Head > shoulder'), (b'33', b'Chin > weak hand'), (b'34', b'Forehead > chest'), (b'35', b'Borst contra'), (b'36', b'Weak hand: palm'), (b'37', b'Back of head'), (b'38', b'Above head'), (b'39', b'Next to trunk'), (b'40', b'Under chin'), (b'41', b'Head > weak hand'), (b'42', b'Borst ipsi'), (b'43', b'Temple'), (b'44', b'Upper leg'), (b'45', b'Leg'), (b'46', b'Mouth ipsi'), (b'47', b'High in neutral space'), (b'48', b'Mouth > chest'), (b'49', b'Chin ipsi'), (b'50', b'Wrist'), (b'51', b'Lip'), (b'52', b'Neck > chest'), (b'53', b'Cheek + chin'), (b'54', b'Upper arm'), (b'55', b'Shoulder contra'), (b'56', b'Forehead > weak hand'), (b'57', b'Neck ipsi'), (b'58', b'Mouth > weak hand'), (b'59', b'Weak hand: thumb side'), (b'60', b'Between thumb and index finger'), (b'61', b'Neutral space: high'), (b'62', b'Chin contra'), (b'63', b'Upper lip'), (b'64', b'Forehead contra'), (b'65', b'Side of upper body'), (b'66', b'Weak hand: tips'), (b'67', b'Mouth + chin'), (b'68', b'Side of head'), (b'69', b'Head > neutral space'), (b'70', b'Chin > chest'), (b'71', b'Face + head'), (b'72', b'Cheek contra'), (b'73', b'Belly ipsi'), (b'74', b'Chest contra'), (b'75', b'Neck contra'), (b'76', b'Back of the head'), (b'77', b'Elbow'), (b'78', b'Temple > chest'), (b'79', b'Thumb'), (b'80', b'Middle finger'), (b'81', b'Pinkie'), (b'82', b'Index finger'), (b'83', b'Back'), (b'84', b'Ear > cheek'), (b'85', b'Knee'), (b'86', b'Shoulder contra > shoulder ipsi'), (b'87', b'Mouth + cheek')])),
                ('final_loc', models.IntegerField(blank=True, null=True, verbose_name=b'Final Primary Location', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('locVirtObj', models.CharField(max_length=50, null=True, verbose_name=b'Virtual Object', blank=True)),
                ('locsecond', models.IntegerField(blank=True, null=True, verbose_name=b'Secondary Location', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('initial_secondary_loc', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'Initial Subordinate Location', choices=[(b'notset', b'No Value Set'), (b'0', b'N/A'), (b'back', b'Back'), (b'palm', b'Palm'), (b'radial', b'Radial'), (b'ulnar', b'Ulnar'), (b'fingertip(s)', b'Fingertips'), (b'root', b'Root')])),
                ('final_secondary_loc', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'Final Subordinate Location', choices=[(b'notset', b'No Value Set'), (b'0', b'N/A'), (b'back', b'Back'), (b'palm', b'Palm'), (b'radial', b'Radial'), (b'ulnar', b'Ulnar'), (b'fingertip(s)', b'Fingertips'), (b'root', b'Root')])),
                ('initial_palm_orientation', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'Initial Palm Orientation', choices=[(b'notset', b'No Value Set'), (b'prone', b'Prone'), (b'neutral', b'Neutral'), (b'supine', b'Supine'), (b'0', b'N/A')])),
                ('final_palm_orientation', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'Final Palm Orientation', choices=[(b'notset', b'No Value Set'), (b'prone', b'Prone'), (b'neutral', b'Neutral'), (b'supine', b'Supine'), (b'0', b'N/A')])),
                ('initial_relative_orientation', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'Initial Interacting Dominant Hand Part', choices=[(b'notset', b'No Value Set'), (b'palm', b'Palm'), (b'back', b'Back'), (b'root', b'Root'), (b'radial', b'Radial'), (b'ulnar', b'Ulnar'), (b'fingertip(s)', b'Fingertips'), (b'0', b'N/A')])),
                ('final_relative_orientation', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'Final Interacting Dominant Hand Part', choices=[(b'notset', b'No Value Set'), (b'palm', b'Palm'), (b'back', b'Back'), (b'root', b'Root'), (b'radial', b'Radial'), (b'ulnar', b'Ulnar'), (b'fingertip(s)', b'Fingertips'), (b'0', b'N/A')])),
                ('inWeb', models.NullBooleanField(default=False, verbose_name=b'In the Web dictionary')),
                ('isNew', models.NullBooleanField(default=False, verbose_name=b'Is this a proposed new sign?')),
                ('inittext', models.CharField(max_length=b'50', blank=True)),
                ('morph', models.CharField(max_length=50, verbose_name=b'Morphemic Analysis', blank=True)),
                ('sedefinetf', models.TextField(null=True, verbose_name=b'Signed English definition available', blank=True)),
                ('segloss', models.CharField(max_length=50, null=True, verbose_name=b'Signed English gloss', blank=True)),
                ('sense', models.IntegerField(help_text=b'If there is more than one sense of a sign enter a number here, all signs with sense>1 will use the same video as sense=1', null=True, verbose_name=b'Sense Number', blank=True)),
                ('sn', models.IntegerField(help_text=b'Sign Number must be a unique integer and defines the ordering of signs in the dictionary', unique=True, null=True, verbose_name=b'Sign Number', blank=True)),
                ('StemSN', models.IntegerField(null=True, blank=True)),
                ('relatArtic', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Relation between Articulators', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('absOriPalm', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Absolute Orientation: Palm', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('absOriFing', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Absolute Orientation: Fingers', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('relOriMov', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Relative Orientation: Movement', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('relOriLoc', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Relative Orientation: Location', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('oriCh', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Orientation Change', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('handCh', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Handshape Change', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'0', 'From open to closed')])),
                ('repeat', models.NullBooleanField(default=False, verbose_name=b'Repeated Movement')),
                ('altern', models.NullBooleanField(default=False, verbose_name=b'Alternating Movement')),
                ('movSh', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Movement Shape', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('movDir', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Movement Direction', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'2', 'Movement Direction')])),
                ('movMan', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Movement Manner', choices=[(b'0', b'-'), (b'1', b'N/A'), (b'2', 'Not gonna tell')])),
                ('contType', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Contact Type', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('phonOth', models.TextField(null=True, verbose_name=b'Phonology Other', blank=True)),
                ('mouthG', models.CharField(max_length=50, verbose_name=b'Mouth Gesture', blank=True)),
                ('mouthing', models.CharField(max_length=50, verbose_name=b'Mouthing', blank=True)),
                ('phonetVar', models.CharField(max_length=50, verbose_name=b'Phonetic Variation', blank=True)),
                ('iconImg', models.CharField(max_length=50, verbose_name=b'Iconic Image', blank=True)),
                ('namEnt', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Named Entity', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('semField', models.CharField(blank=True, max_length=5, null=True, verbose_name=b'Semantic Field', choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('tokNo', models.IntegerField(null=True, verbose_name=b'Total Number of Occurrences', blank=True)),
                ('tokNoSgnr', models.IntegerField(null=True, verbose_name=b'Total Number of Signers Using this Sign', blank=True)),
                ('tokNoA', models.IntegerField(null=True, verbose_name=b'Number of Occurrences in Amsterdam', blank=True)),
                ('tokNoV', models.IntegerField(null=True, verbose_name=b'Number of Occurrences in Voorburg', blank=True)),
                ('tokNoR', models.IntegerField(null=True, verbose_name=b'Number of Occurrences in Rotterdam', blank=True)),
                ('tokNoGe', models.IntegerField(null=True, verbose_name=b'Number of Occurrences in Gestel', blank=True)),
                ('tokNoGr', models.IntegerField(null=True, verbose_name=b'Number of Occurrences in Groningen', blank=True)),
                ('tokNoO', models.IntegerField(null=True, verbose_name=b'Number of Occurrences in Other Regions', blank=True)),
                ('tokNoSgnrA', models.IntegerField(null=True, verbose_name=b'Number of Amsterdam Signers', blank=True)),
                ('tokNoSgnrV', models.IntegerField(null=True, verbose_name=b'Number of Voorburg Signers', blank=True)),
                ('tokNoSgnrR', models.IntegerField(null=True, verbose_name=b'Number of Rotterdam Signers', blank=True)),
                ('tokNoSgnrGe', models.IntegerField(null=True, verbose_name=b'Number of Gestel Signers', blank=True)),
                ('tokNoSgnrGr', models.IntegerField(null=True, verbose_name=b'Number of Groningen Signers', blank=True)),
                ('tokNoSgnrO', models.IntegerField(null=True, verbose_name=b'Number of Other Region Signers', blank=True)),
                ('dialect', models.ManyToManyField(to='dictionary.Dialect')),
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
                ('role', models.CharField(max_length=5, choices=[(b'0', b'-'), (b'1', b'N/A')])),
                ('morpheme', models.ForeignKey(related_name='morphemes', to='dictionary.Gloss')),
                ('parent_gloss', models.ForeignKey(related_name='parent_glosses', to='dictionary.Gloss')),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=20, choices=[(b'0', b'-'), (b'1', b'N/A')])),
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
                ('loan', models.BooleanField(default=False, verbose_name=b'Loan Sign')),
                ('other_lang', models.CharField(max_length=20, verbose_name=b'Related Language')),
                ('other_lang_gloss', models.CharField(max_length=50, verbose_name=b'Gloss in related language')),
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
                ('index', models.IntegerField(verbose_name=b'Index')),
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
