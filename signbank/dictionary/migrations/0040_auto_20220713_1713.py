# Generated by Django 3.2.14 on 2022-07-13 05:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0039_merge_20220704_1221'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lemma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
            ],
            options={
                'verbose_name': 'Lemma',
                'verbose_name_plural': 'Lemmas',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='gloss',
            name='lemma',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dictionary.lemma', verbose_name='Lemma'),
        ),
    ]
