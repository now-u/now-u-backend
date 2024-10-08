# Generated by Django 5.1 on 2024-08-23 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_image_internal_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='alt_text',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='internal_name',
            field=models.CharField(help_text='A name used to identity the image internally in the admin panel', max_length=100, null=True),
        ),
    ]
