from typing import Any
from django.contrib import admin
from django import forms
from django.http.request import HttpRequest
from images.admin import AdminImageWidget

from .models import Cause, LearningResource, Action, Campaign, NewsArticle, Organisation, OrganisationExtraLink, Theme

def split_release_info(fieldsets):
    current_field: list[str] = fieldsets[0][1]['fields']

    release_fields = ('release_at', 'end_at')
    for field in release_fields:
        current_field.remove(field)

    return (
        (None, {
            'fields': current_field,
        }),
        ('Release Info', {
            'fields': release_fields,
        }),
    )

class CauseAdminForm(forms.ModelForm):
    header_image = forms.ImageField(widget=AdminImageWidget)

    class Meta:
        model = Cause
        fields = '__all__'

class CauseAdmin(admin.ModelAdmin):
    readonly_fields = ['header_image_preview']
    list_display = ('title', 'id')
    search_fields = ('title', 'description')
    filter_horizontal = ('themes', 'actions', 'learning_resources', 'campaigns')
    form = CauseAdminForm

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'id')
    search_fields = ('title', 'description')
    filter_horizontal = ('actions', 'learning_resources', 'campaigns')

# TODO Allow search by topic
class ActionAdmin(admin.ModelAdmin):
    class CauseInline(admin.TabularInline):
        model = Cause.actions.through
        extra = 0

    list_display = ('title', 'action_type', 'time', 'active', 'id')
    search_fields = ('title', 'what_description', 'why_description')
    list_filter = ('action_type', 'causes')
    # TODO Show causes on admin list
    filter_horizontal = ('causes',)
    inlines = [CauseInline]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        raw_fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(raw_fieldsets)


class CampaignAdmin(admin.ModelAdmin):
    class CauseInline(admin.TabularInline):
        model = Cause.campaigns.through
        extra = 0

    list_display = ('title', 'short_name', 'active', 'id')
    search_fields = ('title', 'short_name', 'description')
    filter_horizontal = ('actions', 'learning_resources')
    list_filter = ('causes',)
    inlines = [CauseInline]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(fieldsets)

class LearningResourceAdmin(admin.ModelAdmin):
    class CauseInline(admin.TabularInline):
        model = Cause.learning_resources.through
        extra = 0

    list_display = ('title', 'learning_resource_type', 'source', 'time', 'active', 'id')
    search_fields = ('title', 'source')
    list_filter = ('learning_resource_type', 'causes')

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(fieldsets)

class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'id')
    search_fields = ('title', 'source')

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(fieldsets)

class OrganisationExtraLinkInline(admin.TabularInline):
    model = OrganisationExtraLink
    extra = 0

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'active')
    inlines = [OrganisationExtraLinkInline]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        raw_fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(raw_fieldsets)

# Register your models here.
admin.site.register(Cause, CauseAdmin)
admin.site.register(LearningResource, LearningResourceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Theme, ThemeAdmin)
