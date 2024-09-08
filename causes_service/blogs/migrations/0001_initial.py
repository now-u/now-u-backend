# Generated by Django 5.1 on 2024-08-23 21:52

import admin.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('images', '0005_alter_image_alt_text_alter_image_internal_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('release_at', models.DateTimeField(help_text='The date from which this resource should be available in the app. If not provided the resource will not be visible')),
                ('end_at', models.DateTimeField(blank=True, help_text='The date from which this resource should no longer be available in the app. If not provided the reosurce will stay visible after its released', null=True)),
                ('title', models.CharField(max_length=128, unique=True)),
                ('subtitle', models.TextField()),
                ('slug', models.CharField(help_text='The text shown in the url', max_length=128, unique=True)),
                ('reading_time', models.IntegerField()),
                ('body', admin.models.MarkdownField()),
                ('authors', models.ManyToManyField(blank=True, related_name='blogs', to=settings.AUTH_USER_MODEL)),
                ('header_image', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='images.image')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]