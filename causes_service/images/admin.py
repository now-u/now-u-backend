from django.contrib import admin

from images.models import Image

# Register your models here.
admin.site.register(Image)

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.contrib import admin


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" /></a> %s ' % \
                          (image_url, image_url, file_name, 'Change:'))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
