from django.contrib import admin
from unfold.admin import ModelAdmin

from faqs.models import Faq

class FaqAdmin(ModelAdmin):
    list_display = ('question', 'answer')
    search_fields = ('question', 'answer')

admin.site.register(Faq, FaqAdmin)
