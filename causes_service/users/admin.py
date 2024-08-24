from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import User

@admin.register(User)
class UserAdmin(ModelAdmin):
    search_fields = ('email', 'name')
    list_filter = ('is_active', 'date_joined')
    list_display = ('email', 'name', 'is_active', 'date_joined')
    pass
