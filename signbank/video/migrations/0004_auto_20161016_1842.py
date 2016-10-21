# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0003_glossvideo_dataset'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='glossvideo',
            options={'ordering': ['videofile']},
        ),
    ]
