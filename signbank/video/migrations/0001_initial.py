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
                ('videofile', models.FileField(upload_to=b'glossvideo', storage=signbank.video.models.GlossVideoStorage(), verbose_name=b'video file')),
                ('version', models.IntegerField(default=0, verbose_name=b'Version')),
                ('gloss', models.ForeignKey(to='dictionary.Gloss')),
            ],
            bases=(models.Model, signbank.video.models.VideoPosterMixin),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('videofile', models.FileField(upload_to=b'upload', verbose_name=b'Video file in h264 mp4 format')),
            ],
            bases=(models.Model, signbank.video.models.VideoPosterMixin),
        ),
    ]
