# Generated by Django 2.2.11 on 2021-09-18 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_auto_20200125_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='glosslanguage',
            field=models.ForeignKey(default=1, help_text='Language that is used for gloss names', on_delete=django.db.models.deletion.PROTECT, related_name='glosslanguage', to='dictionary.Language', verbose_name='Gloss language'),
            preserve_default=False,
        ),
    ]
