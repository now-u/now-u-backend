# Generated by Django 4.2.2 on 2023-12-18 17:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('causes', '0022_remove_theme_description_alter_campaign_actions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='published_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 18, 17, 59, 31, 874583, tzinfo=datetime.timezone.utc), help_text='The date when this resource was published by the source. The app will show news in published order by default.'),
            preserve_default=False,
        ),
    ]