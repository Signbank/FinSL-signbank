# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=100, verbose_name='URL', db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('title_fi', models.CharField(max_length=200, null=True, verbose_name='title')),
                ('title_en', models.CharField(max_length=200, null=True, verbose_name='title')),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('content_fi', models.TextField(null=True, verbose_name='content', blank=True)),
                ('content_en', models.TextField(null=True, verbose_name='content', blank=True)),
                ('template_name', models.CharField(help_text="Example: 'pages/contact_page.html'. If this isn't provided, the system will use 'pages/default.html'.", max_length=70, verbose_name='template name', blank=True)),
                ('publish', models.BooleanField(help_text='If this is checked, the page will be included in the site menus.', verbose_name='publish')),
                ('index', models.IntegerField(default=0, help_text='Used to order pages in the menu', verbose_name='ordering index')),
                ('group_required', models.ManyToManyField(help_text='This page will only be visible to members of these groups, leave blank to allow anyone to access.', to='auth.Group', blank=True)),
                ('parent', models.ForeignKey(blank=True, to='pages.Page', help_text='Leave blank for a top level menu entry.  Top level entries that have sub-pages should be empty as they will not be linked in the menu.', null=True)),
            ],
            options={
                'ordering': ('url', 'index'),
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
            },
        ),
        migrations.CreateModel(
            name='PageVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('number', models.PositiveIntegerField(verbose_name='number')),
                ('video', models.FileField(upload_to=b'pages', blank=True)),
                ('page', models.ForeignKey(to='pages.Page')),
            ],
        ),
    ]
