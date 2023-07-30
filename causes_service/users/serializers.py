from typing import Any
from rest_framework import serializers
from rest_framework.relations import method_overridden

from users.models import User
from utils.serializers import get_user_from_context

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'email', 'name']
        read_only_fields = ['email']

class CausesUserSerializer(serializers.ModelSerializer):
    selected_causes_ids = serializers.SerializerMethodField()
    completed_action_ids = serializers.SerializerMethodField()
    completed_learning_resource_ids = serializers.SerializerMethodField()
    completed_campaign_ids = serializers.SerializerMethodField()

    new_selected_causes_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    def get_completed_action_ids(self, obj: User) -> list[int]:
        return obj.completed_actions.all().values_list("action__pk", flat=True)

    def get_completed_learning_resource_ids(self, obj: User) -> list[int]:
        return obj.completed_learning_resources.all().values_list("learning_resource__pk", flat=True)

    def get_selected_causes_ids(self, obj: User) -> list[int]:
        return obj.selected_causes.all().values_list("cause__pk", flat=True)

    def get_completed_campaign_ids(self, obj: User) -> list[int]:
        return obj.completed_campaigns.all().values_list("campaign__pk", flat=True)

    def _update_selected_causes(self, validated_data: dict):
        user = get_user_from_context(self.context)
        if (user is None):
            raise Exception("User Serializer requires user for create")

        selected_causes_ids = validated_data.pop('new_selected_causes_ids', None)
        if selected_causes_ids is not None:
            user.set_selected_causes(selected_causes_ids)

    def create(self, validated_data: Any) -> Any:
        self._update_selected_causes(validated_data)
        return super().create(validated_data)

    def update(self, instance: Any, validated_data: Any) -> Any:
        self._update_selected_causes(validated_data)
        return super().update(instance, validated_data)

    # def get_selected_causes_ids(self):
    #     user = get_user_from_context(self.context)
    #     return user.selected_causes.all().values_list("pk", flat=True)

    class Meta:
        model = User
        fields = ['id', 'completed_learning_resource_ids', 'completed_action_ids', 'selected_causes_ids', 'completed_campaign_ids', 'new_selected_causes_ids']

