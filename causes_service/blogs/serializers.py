from rest_framework import serializers

from images.serializers import ImageSerializer
from users.models import User
from .models import Blog

class AuthorSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source="blog_profile_description")
    picture = ImageSerializer(source="blog_profile_picture")

    class Meta:
        model = User
        fields = ['id', 'name', 'description', 'picture']

class BlogSerializer(serializers.ModelSerializer):
    release_at_timestamp = serializers.IntegerField()
    authors = AuthorSerializer(many=True)
    header_image = ImageSerializer()

    class Meta:
        model = Blog
        fields = '__all__'
        lookup_field = 'slug'
