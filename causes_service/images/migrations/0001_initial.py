# Generated by Django 4.2.2 on 2023-07-22 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to='')),
                ('alt_text', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
