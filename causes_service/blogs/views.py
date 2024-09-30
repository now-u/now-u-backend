from django.utils import timezone
from rest_framework import viewsets

from .models import Blog
from .serializers import BlogSerializer

class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Blog.objects.filter_active(is_active_at=timezone.now()).order_by('-release_at')

