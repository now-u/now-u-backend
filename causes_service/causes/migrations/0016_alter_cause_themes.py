# Generated by Django 4.2.2 on 2023-07-29 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('causes', '0015_cause_themes_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cause',
            name='themes',
            field=models.ManyToManyField(blank=True, related_name='causes', to='causes.theme'),
        ),
    ]
