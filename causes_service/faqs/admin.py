from django.contrib import admin

from faqs.models import Faq

class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer')

admin.site.register(Faq, FaqAdmin)
