from django.db import models

def _image_path(instance, filename):
    return f'images/{instance.pk}-{filename}'

class Image(models.Model):
    image = models.ImageField(upload_to=_image_path)
    alt_text = models.CharField(max_length=100, null=True, blank=True)
