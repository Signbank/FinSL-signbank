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
                ('user', models.OneToOneField(verbose_name='user', to=settings.AUTH_USER_MODEL)),
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
                ('yob', models.IntegerField(verbose_name='When were you born?')),
                ('australian', models.BooleanField(verbose_name='Do you live in Finland?')),
                ('postcode', models.CharField(max_length=20, verbose_name='If you live in Finland, what is your postcode?', blank=True)),
                ('background', models.CommaSeparatedIntegerField(max_length=20, verbose_name='What is your background?', choices=[(0, 'deaf community'), (1, 'FinSL teacher'), (2, 'teacher of the deaf'), (3, 'parent of a deaf child'), (4, 'sign language interpreter'), (5, 'school or university student'), (6, 'student learning FinSL'), (7, 'other')])),
                ('auslan_user', models.BooleanField(verbose_name='Do you use FinSL?')),
                ('learned', models.IntegerField(verbose_name='If you use FinSL, when did you learn sign language?', choices=[(0, 'Not Applicable'), (1, 'At home from my parent(s)'), (2, 'At kindergarten or at the beginning of primary school'), (3, 'At primary school'), (4, 'At high school'), (5, 'After I left school')])),
                ('deaf', models.BooleanField(verbose_name='Are you a deaf person?')),
                ('schooltype', models.IntegerField(verbose_name='What sort of school do you (or did you) attend?', choices=[(0, 'a deaf school (boarder)'), (1, 'a deaf school (day student)'), (2, 'a deaf classroom or unit in a hearing school'), (3, 'a regular classroom in a hearing school')])),
                ('school', models.CharField(max_length=50, verbose_name='Which school do you (or did you) attend?', blank=True)),
                ('teachercomm', models.IntegerField(verbose_name='How do (or did) your teachers communicate with you?', choices=[(0, 'mostly oral'), (1, 'mostly Signed English'), (2, 'mostly sign language (FinSL)'), (3, 'mostly fingerspelling')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
