from django.apps import AppConfig

# TODO Rename faq app to faqs and renmae all FAQ to Faq
class FaqConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faqs'
