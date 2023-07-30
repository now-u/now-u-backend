from django.contrib import admin
from .models import Cause, LearningResource, Action, Campaign, NewsArticle, Organisation, OrganisationExtraLink, Theme

class CauseAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title', 'description')
    filter_horizontal = ('themes', 'actions', 'learning_resources', 'campaigns')

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'id')
    search_fields = ('title', 'description')
    filter_horizontal = ('actions', 'learning_resources', 'campaigns')

# TODO Allow search by topic
class ActionAdmin(admin.ModelAdmin):
    list_display = ('title', 'action_type', 'time', 'active', 'id')
    search_fields = ('title', 'what_description', 'why_description')
    list_filter = ('action_type',)
    # TODO Show causes on admin list
    filter_horizontal = ('causes',)

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name', 'active', 'id')
    search_fields = ('title', 'short_name', 'description')
    filter_horizontal = ('actions', 'learning_resources')

class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'learning_resource_type', 'source', 'time', 'active', 'id')
    search_fields = ('title', 'source')
    list_filter = ('learning_resource_type',)

class OrganisationExtraLinkInline(admin.TabularInline):
    model = OrganisationExtraLink
    extra = 0

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    inlines = [OrganisationExtraLinkInline]

# Register your models here.
admin.site.register(Cause, CauseAdmin)
admin.site.register(LearningResource, LearningResourceAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(NewsArticle)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Theme, ThemeAdmin)
