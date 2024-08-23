from rest_framework import serializers

from images.models import Image

class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj: Image) -> str:
        return obj.get_url()

    class Meta:
        model = Image
        fields = ['id', 'url', 'alt_text']
