# Generated by Django 2.2.11 on 2022-06-06 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0020_merge_20220602_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gloss',
            name='number_incorporated',
            field=models.BooleanField(default=False, verbose_name='Number incorporated'),
        ),
    ]