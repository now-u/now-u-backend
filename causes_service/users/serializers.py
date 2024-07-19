from typing import Any
from rest_framework import serializers

from users.models import User
from causes.models import Cause

class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=1, max_length=150)

    def update(self, instance, validated_data: Any):
        return super().update(instance, validated_data)

    class Meta:
        model = User
        fields = ['id', 'email', 'name']
        read_only_fields = ['email']

class CausesUserSerializer(serializers.ModelSerializer):
    selected_causes_ids = serializers.PrimaryKeyRelatedField(many=True, source='selected_causes', queryset=Cause.objects.all())
    completed_action_ids = serializers.SerializerMethodField()
    completed_learning_resource_ids = serializers.SerializerMethodField()
    completed_campaign_ids = serializers.SerializerMethodField()
    completed_news_article_ids = serializers.SerializerMethodField()

    def get_completed_action_ids(self, obj: User) -> list[int]:
        return obj.completed_actions.all().values_list("action__pk", flat=True)

    def get_completed_learning_resource_ids(self, obj: User) -> list[int]:
        return obj.completed_learning_resources.all().values_list("learning_resource__pk", flat=True)

    def get_completed_campaign_ids(self, obj: User) -> list[int]:
        return obj.completed_campaigns.all().values_list("campaign__pk", flat=True)

    def get_completed_news_article_ids(self, obj: User) -> list[int]:
        return obj.completed_news_articles.all().values_list("news_article__pk", flat=True)

    class Meta:
        model = User
        fields = ['id', 'completed_learning_resource_ids', 'completed_action_ids', 'selected_causes_ids', 'completed_campaign_ids', 'completed_news_article_ids']

