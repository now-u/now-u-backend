from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

def _image_path(instance, filename):
    return f'images/{instance.pk}-{filename}'

class Image(models.Model):
    image = models.ImageField(upload_to=_image_path)
    alt_text = models.CharField(max_length=100, null=True, blank=True)
    internal_name = models.CharField(max_length=100, null=True, blank=True, help_text=_('A name used to identity the image internally in the admin panel'))

    def image_preview(self):
        return format_html(f'<img src = "{self.image.url}" width = "300"/>')

    def __str__(self) -> str:
        name = self.internal_name or self.alt_text
        if name:
            return f"{self.pk} - {name}"
        return str(self.pk)
