# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0005_glossvideo_posterfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='glossvideo',
            name='title',
            field=models.CharField(help_text='Descriptive title of the contents of the video', max_length=100, blank=True),
        ),
    ]
