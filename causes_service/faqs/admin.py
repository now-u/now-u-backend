from django.contrib import admin

from faqs.models import Faq

class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer')
    search_fields = ('question', 'answer')

admin.site.register(Faq, FaqAdmin)
