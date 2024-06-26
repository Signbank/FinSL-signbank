# Generated by Django 3.2.18 on 2024-05-09 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlatPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(db_index=True, max_length=100, verbose_name='URL')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('title_fi', models.CharField(max_length=200, null=True, verbose_name='title')),
                ('title_sv', models.CharField(max_length=200, null=True, verbose_name='title')),
                ('title_en', models.CharField(max_length=200, null=True, verbose_name='title')),
                ('content', models.TextField(blank=True, verbose_name='content')),
                ('content_fi', models.TextField(blank=True, null=True, verbose_name='content')),
                ('content_sv', models.TextField(blank=True, null=True, verbose_name='content')),
                ('content_en', models.TextField(blank=True, null=True, verbose_name='content')),
                ('enable_comments', models.BooleanField(default=False, verbose_name='enable comments')),
                ('template_name', models.CharField(blank=True, help_text='Example: “flatpages/contact_page.html”. If this isn’t provided, the system will use “flatpages/default.html”.', max_length=70, verbose_name='template name')),
                ('registration_required', models.BooleanField(default=False, help_text='If this is checked, only logged-in users will be able to view the page.', verbose_name='registration required')),
                ('sites', models.ManyToManyField(to='sites.Site', verbose_name='sites')),
            ],
            options={
                'verbose_name': 'flat page',
                'verbose_name_plural': 'flat pages',
                'db_table': 'django_flatpage',
                'ordering': ['url'],
            },
        ),
    ]
