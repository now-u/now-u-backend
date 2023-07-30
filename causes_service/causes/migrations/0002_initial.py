# Generated by Django 4.2.2 on 2023-07-22 23:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('causes', '0001_initial'),
        ('images', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userlearningresources',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_learning_resources', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usercause',
            name='cause',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='causes.cause'),
        ),
        migrations.AddField(
            model_name='usercause',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selected_causes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usercampaign',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='causes.campaign'),
        ),
        migrations.AddField(
            model_name='usercampaign',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_campaigns', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='useraction',
            name='action',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='causes.action'),
        ),
        migrations.AddField(
            model_name='useraction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_actions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organisationextralink',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extra_links', to='causes.organisation'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='logo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.image'),
        ),
        migrations.AddField(
            model_name='newsarticle',
            name='header_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.image'),
        ),
        migrations.AddField(
            model_name='cause',
            name='actions',
            field=models.ManyToManyField(blank=True, related_name='causes', to='causes.action'),
        ),
        migrations.AddField(
            model_name='cause',
            name='campaigns',
            field=models.ManyToManyField(blank=True, related_name='causes', to='causes.campaign'),
        ),
        migrations.AddField(
            model_name='cause',
            name='header_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.image'),
        ),
        migrations.AddField(
            model_name='cause',
            name='learning_resources',
            field=models.ManyToManyField(blank=True, related_name='causes', to='causes.learningresource'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='actions',
            field=models.ManyToManyField(related_name='campaigns', to='causes.action'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='header_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.image'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='learning_resources',
            field=models.ManyToManyField(related_name='campaigns', to='causes.learningresource'),
        ),
    ]
