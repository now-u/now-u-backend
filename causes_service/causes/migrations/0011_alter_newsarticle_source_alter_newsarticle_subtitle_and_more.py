# Generated by Django 4.2.2 on 2023-07-29 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('causes', '0010_alter_learningresource_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='source',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='newsarticle',
            name='subtitle',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='newsarticle',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
