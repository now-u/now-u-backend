from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

from images.models import Image

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'internal_name', 'alt_text',)
    search_fields = ('internal_name', 'alt_text',)

admin.site.register(Image, ImageAdmin)

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, **kwargs):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" /></a> %s ' % \
                          (image_url, image_url, file_name, 'Change:'))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
