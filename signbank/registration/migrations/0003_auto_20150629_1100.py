# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_auto_20150625_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='auslan_user',
            field=models.BooleanField(verbose_name='Do you use FinSL?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='background',
            field=models.CommaSeparatedIntegerField(max_length=20, verbose_name='What is your background?', choices=[(0, 'deaf community'), (1, 'FinSL teacher'), (2, 'teacher of the deaf'), (3, 'parent of a deaf child'), (4, 'sign language interpreter'), (5, 'school or university student'), (6, 'student learning FinSL'), (7, 'other')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='learned',
            field=models.IntegerField(verbose_name='If you use FinSL, when did you learn sign language?', choices=[(0, 'Not Applicable'), (1, 'At home from my parent(s)'), (2, 'At kindergarten or at the beginning of primary school'), (3, 'At primary school'), (4, 'At high school'), (5, 'After I left school')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='teachercomm',
            field=models.IntegerField(verbose_name='How do (or did) your teachers communicate with you?', choices=[(0, 'mostly oral'), (1, 'mostly Signed English'), (2, 'mostly sign language (FinSL)'), (3, 'mostly fingerspelling')]),
        ),
    ]
