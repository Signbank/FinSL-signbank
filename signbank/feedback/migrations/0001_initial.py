# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(blank=True)),
                ('video', models.FileField(upload_to=b'comments', blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'unread', max_length=10, choices=[(b'unread', b'unread'), (b'read', b'read'), (b'deleted', b'deleted')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='InterpreterFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(verbose_name=b'Note')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'unread', max_length=10, choices=[(b'unread', b'unread'), (b'read', b'read'), (b'deleted', b'deleted')])),
                ('gloss', models.ForeignKey(to='dictionary.Gloss')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'permissions': (('view_interpreterfeedback', 'Can View Interpreter Feedback'),),
            },
        ),
        migrations.CreateModel(
            name='MissingSignFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('handform', models.IntegerField(default=0, blank=True, choices=[(1, 'One handed'), (2, 'Two handed (same shape for each hand)'), (3, 'Two handed (diffent shapes for each hand)')])),
                ('handshape', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (291, 'Animal'), (292, 'Animal-flick'), (293, 'Bad'), (294, 'Ball'), (295, 'Cup'), (296, 'Cup-flush'), (297, 'Cup-thumb'), (298, 'Eight'), (299, 'Eight-hook'), (300, 'Fist-A'), (301, 'Fist-S'), (302, 'Flat'), (303, 'Flat-bent'), (304, 'Flat-B'), (305, 'Flat-flush'), (306, 'Flick'), (307, 'Flick-gay'), (308, 'Four'), (309, 'Five'), (310, 'Good'), (311, 'Good-6'), (312, 'Gun'), (313, 'Gun-hook'), (314, 'Hook'), (315, 'Kneel'), (316, 'Letter-C'), (317, 'Letter-M'), (318, 'Letter-N'), (319, 'Love'), (320, 'Middle'), (321, 'Mother'), (322, 'Nine'), (323, 'Point-1'), (324, 'Point-D'), (325, 'Point-flush'), (326, 'Okay-flat'), (327, 'Okay-F'), (328, 'Okay-O'), (329, 'Old-seven'), (330, 'Plane'), (331, 'Perth'), (332, 'Round-O'), (333, 'Round-flat'), (334, 'Round-E'), (335, 'Rude'), (336, 'Salt'), (337, 'Salt-flick'), (338, 'Small'), (339, 'Soon'), (340, 'Spoon'), (341, 'Spoon-hook'), (342, 'Spoon-thumb'), (343, 'Thick'), (344, 'Three'), (345, 'Three-hook'), (346, 'Two'), (347, 'Wish'), (348, 'Write'), (349, 'Write-flat')])),
                ('althandshape', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (291, 'Animal'), (292, 'Animal-flick'), (293, 'Bad'), (294, 'Ball'), (295, 'Cup'), (296, 'Cup-flush'), (297, 'Cup-thumb'), (298, 'Eight'), (299, 'Eight-hook'), (300, 'Fist-A'), (301, 'Fist-S'), (302, 'Flat'), (303, 'Flat-bent'), (304, 'Flat-B'), (305, 'Flat-flush'), (306, 'Flick'), (307, 'Flick-gay'), (308, 'Four'), (309, 'Five'), (310, 'Good'), (311, 'Good-6'), (312, 'Gun'), (313, 'Gun-hook'), (314, 'Hook'), (315, 'Kneel'), (316, 'Letter-C'), (317, 'Letter-M'), (318, 'Letter-N'), (319, 'Love'), (320, 'Middle'), (321, 'Mother'), (322, 'Nine'), (323, 'Point-1'), (324, 'Point-D'), (325, 'Point-flush'), (326, 'Okay-flat'), (327, 'Okay-F'), (328, 'Okay-O'), (329, 'Old-seven'), (330, 'Plane'), (331, 'Perth'), (332, 'Round-O'), (333, 'Round-flat'), (334, 'Round-E'), (335, 'Rude'), (336, 'Salt'), (337, 'Salt-flick'), (338, 'Small'), (339, 'Soon'), (340, 'Spoon'), (341, 'Spoon-hook'), (342, 'Spoon-thumb'), (343, 'Thick'), (344, 'Three'), (345, 'Three-hook'), (346, 'Two'), (347, 'Wish'), (348, 'Write'), (349, 'Write-flat')])),
                ('location', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (257, 'Top of head'), (258, 'Forehead'), (259, 'Temple'), (260, 'Eyes'), (261, 'Nose'), (262, 'Whole of face'), (263, 'Cheekbone'), (264, 'Ear'), (265, 'Cheek'), (266, 'Mouth and lips'), (267, 'Chin'), (268, 'Neck'), (269, 'Shoulder'), (270, 'Chest'), (271, 'Stomach'), (272, 'Waist'), (273, 'Lower waist'), (274, 'Upper arm'), (275, 'Elbow')])),
                ('relativelocation', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (283, 'Forearm'), (284, 'Wrist'), (285, 'Pulse'), (286, 'Back of hand'), (287, 'Palm'), (288, 'Sides of hand'), (289, 'Fingertips')])),
                ('handbodycontact', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (240, 'Contact at start of movement'), (241, 'Contact at end of movement'), (242, 'Two contacts (tap)'), (243, 'Contact during (rub/stroke)')])),
                ('handinteraction', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (468, 'Alternate hands (one moves, then the other moves)'), (469, 'Move the hands towards each other'), (470, 'Move the hands away from each other'), (471, 'The hands cross over each other')])),
                ('direction', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (472, 'Up'), (473, 'Down'), (474, 'Up and down'), (475, 'Left'), (476, 'Right'), (477, 'Side to side'), (478, 'Away'), (479, 'Towards'), (480, 'To and fro')])),
                ('movementtype', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (481, 'Straight'), (482, 'Curved'), (483, 'Circle'), (484, 'Zig-zag')])),
                ('smallmovement', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (485, 'Straighten from bent'), (486, 'Bend fingers'), (487, 'Nod at wrist'), (488, 'Straighten fingers'), (489, 'Open handshape'), (490, 'Close handshape'), (491, 'Wriggle fingers'), (492, 'Crumble fingers')])),
                ('repetition', models.IntegerField(default=0, blank=True, choices=[(0, 'Ei arvoa'), (493, 'Do the movement once'), (494, 'Do the movement twice'), (495, 'Repeat the movement several times')])),
                ('meaning', models.TextField()),
                ('comments', models.TextField(blank=True)),
                ('video', models.FileField(upload_to=b'comments', blank=True)),
                ('status', models.CharField(default=b'unread', max_length=10, choices=[(b'unread', b'unread'), (b'read', b'read'), (b'deleted', b'deleted')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='SignFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(verbose_name='Please give us your comments about this sign. For example: do you think there are other keywords that belong with this sign? Please write your comments or new keyword/s below.', blank=True)),
                ('kwnotbelong', models.TextField(verbose_name='Is there a keyword or keyword/s that DO NOT belong with this sign? Please provide the list of keywords below', blank=True)),
                ('isAuslan', models.IntegerField(verbose_name='Is this sign an FIN Sign?', choices=[(1, 'yes'), (2, 'Perhaps'), (3, "Don't know"), (4, "Don't think so"), (5, 'Ei'), (0, 'N/A')])),
                ('whereused', models.CharField(max_length=10, verbose_name='Where is this sign used?', choices=[(b'auswide', b'Australia Wide'), (b'dialectN', b'Dialect Sign (North)'), (b'dialectS', b'Dialect Sign (South)'), (b'nsw', b'New South Wales'), (b'vic', b'Victoria'), (b'qld', b'Queensland'), (b'wa', b'Western Australia'), (b'sa', b'South Australia'), (b'tas', b'Tasmania'), (b'nt', b'Northern Territory'), (b'act', b'Australian Capital Territory'), (b'dk', b"Don't Know"), (b'n/a', b'N/A')])),
                ('like', models.IntegerField(verbose_name='Do you like this sign?', choices=[(1, 'yes'), (2, 'A little'), (3, "Don't care"), (4, 'Not much'), (5, 'Ei'), (0, 'N/A')])),
                ('use', models.IntegerField(verbose_name='Do you use this sign?', choices=[(1, 'yes'), (2, 'Sometimes'), (3, 'Not Often'), (4, 'Ei'), (0, 'N/A')])),
                ('suggested', models.IntegerField(default=3, verbose_name='If this sign is a suggested new sign, would you use it?', choices=[(1, 'yes'), (2, 'Sometimes'), (3, "Don't Know"), (4, 'Perhaps'), (5, 'Ei'), (0, 'N/A')])),
                ('correct', models.IntegerField(verbose_name='Is the information about the sign correct?', choices=[(1, 'yes'), (2, 'Mostly Correct'), (3, "Don't Know"), (4, 'Mostly Wrong'), (5, 'Ei'), (0, 'N/A')])),
                ('status', models.CharField(default=b'unread', max_length=10, choices=[(b'unread', b'unread'), (b'read', b'read'), (b'deleted', b'deleted')])),
                ('translation', models.ForeignKey(editable=False, to='dictionary.Translation')),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
