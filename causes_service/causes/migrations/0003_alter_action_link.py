# Generated by Django 4.2.2 on 2023-07-26 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('causes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='link',
            field=models.URLField(max_length=300),
        ),
    ]
