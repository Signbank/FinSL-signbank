# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0012_auto_20150618_0910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gloss',
            name='locVirtObj',
        ),
    ]
