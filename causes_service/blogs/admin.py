from django.contrib import admin
from unfold.admin import ModelAdmin, FieldsetsType
from django.http.request import HttpRequest

from admin.models import MarkdownField
from admin.widgets import MarkdownEditorWidget
from admin.utils import split_release_info

from .models import Blog

@admin.register(Blog)
class BlogAdmin(ModelAdmin):
    formfield_overrides = {
        MarkdownField: {"widget": MarkdownEditorWidget},
    }
    filter_horizontal = ('authors', )

    def get_fieldsets(self, request: HttpRequest, obj=None) -> FieldsetsType:
        raw_fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(raw_fieldsets)
