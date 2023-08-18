from django.db import models
from django.utils.html import format_html

def _image_path(instance, filename):
    return f'images/{instance.pk}-{filename}'

class Image(models.Model):
    image = models.ImageField(upload_to=_image_path)
    alt_text = models.CharField(max_length=100, null=True, blank=True)

    def image_preview(self):
        return format_html(f'<img src = "{self.image.url}" width = "300"/>')
