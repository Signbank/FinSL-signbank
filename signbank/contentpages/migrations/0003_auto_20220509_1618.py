# Generated by Django 2.2.11 on 2022-05-09 04:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0002_add_modeltranslation_fields_to_flatpages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flatpage',
            name='content_fi',
        ),
        migrations.RemoveField(
            model_name='flatpage',
            name='title_fi',
        ),
    ]