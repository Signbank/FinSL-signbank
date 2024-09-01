# Generated by Django 3.2.18 on 2024-09-01 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_glossurl_sign_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='show_comments_in_public',
            field=models.BooleanField(default=True, help_text='Show comments in public interface?', verbose_name='Show Gloss comments in public interface'),
        ),
    ]