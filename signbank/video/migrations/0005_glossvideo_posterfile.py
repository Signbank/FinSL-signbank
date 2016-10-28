# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import signbank.video.models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0004_auto_20161016_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='glossvideo',
            name='posterfile',
            field=models.FileField(storage=signbank.video.models.GlossVideoStorage(), upload_to=b'glossvideo/posters', null=True, verbose_name=b'Poster file'),
        ),
    ]
