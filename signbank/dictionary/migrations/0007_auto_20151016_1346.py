# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dictionary', '0006_auto_20150828_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='gloss',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 16, 10, 42, 32, 21149, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gloss',
            name='created_by',
            field=models.ForeignKey(related_name='created_by_user', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gloss',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 16, 10, 45, 56, 193255, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gloss',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_by_user', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
