# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import signbank.video.models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlossVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('videofile', models.FileField(upload_to='glossvideo', storage=signbank.video.models.GlossVideoStorage(), verbose_name='video file')),
                ('version', models.IntegerField(default=0, verbose_name='Version')),
                ('gloss', models.ForeignKey(to='dictionary.Gloss')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('videofile', models.FileField(upload_to='upload', verbose_name='Video file in h264 mp4 format')),
            ],
        ),
    ]
