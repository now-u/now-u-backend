from rest_framework import viewsets

from faqs.models import Faq
from faqs.serializers import FaqSerializer


class FaqViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer
