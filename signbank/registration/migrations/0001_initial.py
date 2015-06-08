# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activation_key', models.CharField(max_length=40, verbose_name='activation key')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'verbose_name': 'registration profile',
                'verbose_name_plural': 'registration profiles',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yob', models.IntegerField(verbose_name=b'When were you born?')),
                ('australian', models.BooleanField(verbose_name=b'Do you live in Finland?')),
                ('postcode', models.CharField(max_length=20, verbose_name=b'If you live in Finland, what is your postcode?', blank=True)),
                ('background', models.CommaSeparatedIntegerField(max_length=20, verbose_name=b'What is your background?', choices=[(0, b'deaf community'), (1, b'FIN teacher'), (2, b'teacher of the deaf'), (3, b'parent of a deaf child'), (4, b'sign language interpreter'), (5, b'school or university student'), (6, b'student learning FIN'), (7, b'other')])),
                ('auslan_user', models.BooleanField(verbose_name=b'Do you use FIN?')),
                ('learned', models.IntegerField(verbose_name=b'If you use FIN, when did you learn sign language?', choices=[(0, b'Not Applicable'), (1, b'At home from my parent(s)'), (2, b'At kindergarten or at the beginning of primary school'), (3, b'At primary school'), (4, b'At high school'), (5, b'After I left school')])),
                ('deaf', models.BooleanField(verbose_name=b'Are you a deaf person?')),
                ('schooltype', models.IntegerField(verbose_name=b'What sort of school do you (or did you) attend?', choices=[(0, b'a deaf school (boarder)'), (1, b'a deaf school (day student)'), (2, b'a deaf classroom or unit in a hearing school'), (3, b'a regular classroom in a hearing school')])),
                ('school', models.CharField(max_length=50, verbose_name=b'Which school do you (or did you) attend?', blank=True)),
                ('teachercomm', models.IntegerField(verbose_name=b'How do (or did) your teachers communicate with you?', choices=[(0, b'mostly oral'), (1, b'mostly Signed English'), (2, b'mostly sign language (FIN)'), (3, b'mostly fingerspelling')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
    ]
