from rest_framework import viewsets

from .models import Blog
from .serializers import BlogSerializer

class CauseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
