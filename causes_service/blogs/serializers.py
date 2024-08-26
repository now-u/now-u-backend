from rest_framework import serializers

from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    release_at_timestamp = serializers.IntegerField()

    class Meta:
        model = Blog
        fields = '__all__'
