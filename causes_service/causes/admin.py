from django.utils import timezone
from datetime import datetime
from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import Cause, LearningResource, Action, Campaign, NewsArticle, Organisation, OrganisationExtraLink, Theme, filter_active_for_releaseable_queryset

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

class ActiveListFilter(admin.SimpleListFilter):
    title = _("Active")
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return [
            ("Active", _("Active (visible on the app)")),
            ("Inavtive", _("Inacvtive (not visible on the app)")),
        ]

    def queryset(self, request, queryset):
        now = datetime.utcnow()
        if self.value() == "Active":
            return filter_active_for_releaseable_queryset(queryset, is_active_at=now, is_active=True)
        elif self.value() == "Inavtive":
            return filter_active_for_releaseable_queryset(queryset, is_active_at=now, is_active=False)
        return queryset

@admin.action(description="Set end date of the release to now (hide the resources)")
def end_now_action(modeladmin, request, queryset):
    queryset.update(end_at=timezone.now())

# class CauseAdminForm(forms.ModelForm):
#     # TODO Add image preview
#     # header_image = forms.ImageField(widget=AdminImageWidget)
#     class Meta:
#         model = Cause
#         fields = '__all__'

class CauseAdmin(admin.ModelAdmin):
    # readonly_fields = ['header_image_preview']
    list_display = ('title', 'id')
    search_fields = ('title', 'description')
    filter_horizontal = ('themes', 'actions', 'learning_resources', 'campaigns', 'news_articles')
    # form = CauseAdminForm

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title',)
    filter_horizontal = ('campaigns',)

# TODO Allow search by topic
class ActionAdmin(admin.ModelAdmin):
    class CauseInline(admin.TabularInline):
        model = Cause.actions.through
        extra = 0

    list_display = ('title', 'action_type', 'time', 'active', 'id')
    search_fields = ('title', 'what_description', 'why_description')
    list_filter = ('action_type', 'causes', ActiveListFilter)
    # TODO Show causes on admin list
    filter_horizontal = ('causes',)
    inlines = [CauseInline]
    actions = [end_now_action]

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
    list_filter = ('causes', ActiveListFilter)
    inlines = [CauseInline]
    actions = [end_now_action]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(fieldsets)

class LearningResourceAdmin(admin.ModelAdmin):
    class CauseInline(admin.TabularInline):
        model = Cause.learning_resources.through
        extra = 0

    list_display = ('title', 'learning_resource_type', 'source', 'time', 'active', 'id')
    search_fields = ('title', 'source')
    list_filter = ('learning_resource_type', 'causes', ActiveListFilter)
    actions = [end_now_action]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(fieldsets)

class NewsArticleAdmin(admin.ModelAdmin):
    class CauseInline(admin.TabularInline):
        model = Cause.news_articles.through
        extra = 0

    list_display = ('title', 'source', 'active', 'id')
    search_fields = ('title', 'source')
    list_filter = ('causes', ActiveListFilter)
    actions = [end_now_action]
    inlines = [CauseInline]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fieldsets = super().get_fieldsets(request, obj)
        return split_release_info(fieldsets)

class OrganisationExtraLinkInline(admin.TabularInline):
    model = OrganisationExtraLink
    extra = 0

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'active')
    search_fields = ('name',)
    list_filter = (ActiveListFilter,)
    inlines = [OrganisationExtraLinkInline]
    actions = [end_now_action]

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
