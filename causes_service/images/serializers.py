from rest_framework import serializers

from images.models import Image
from now_u_api.settings import BASE_URL, USING_AZURE_STORAGE

class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj) -> str:
        if not USING_AZURE_STORAGE:
            return f"{BASE_URL}{obj.image.url}"
        return obj.image.url

    class Meta:
        model = Image
        fields = ['id', 'url', 'alt_text']
