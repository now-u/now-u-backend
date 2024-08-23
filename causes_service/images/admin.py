from typing import cast
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from unfold.admin import ModelAdmin

from images.models import Image

class ImageAdmin(ModelAdmin):
    list_display = ('id', 'internal_name', 'alt_text',)
    search_fields = ('internal_name', 'alt_text',)

    def response_add(self, request, obj, post_url_continue=None):
        image: Image = cast(Image, obj)
        if "_markdown_field_id" in request.GET:
            return TemplateResponse(
                request,
                "markdown_image_upload_response.html",
                {
                    "markdown_field_id": request.GET.get('_markdown_field_id'),
                    "image_url": image.get_url(),
                    "alt_text": image.alt_text,
                },
            )

        return super().response_add(request, obj, post_url_continue)

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
