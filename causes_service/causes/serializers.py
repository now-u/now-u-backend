from rest_framework import serializers

from images.serializers import ImageSerializer
from .models import Cause, LearningResource, Action, Campaign, NewsArticle, Organisation, OrganisationExtraLink
from utils.serializers import get_user_from_context

class CauseSerializer(serializers.ModelSerializer):
    is_selected = serializers.SerializerMethodField()
    header_image = ImageSerializer()

    def get_is_selected(self, obj: Cause) -> bool:
        user = get_user_from_context(self.context)
        if user is None:
            return False
        return obj.is_selected(user.pk)

    class Meta:
        model = Cause
        # TODO Selected, icon
        fields = ['id', 'title', 'header_image', 'icon', 'description', 'is_selected']

class ListActionSerializer(serializers.ModelSerializer):
    causes = CauseSerializer(many=True)

    class Meta:
        model = Action
        # TODO Completed
        fields = ['id', 'title', 'action_type', 'causes', 'time', 'created_at', 'release_at', 'of_the_month', 'suggested']

class LearningResourceSerializer(serializers.ModelSerializer):
    causes = CauseSerializer(many=True)

    class Meta:
        model = LearningResource
        # TODO
        fields = '__all__'

class ListCampaignSerializer(serializers.ModelSerializer):
    causes = CauseSerializer(many=True)
    header_image = ImageSerializer()

    class Meta:
        model = Campaign
        # TODO
        fields = ['id', 'title', 'short_name', 'causes', 'header_image', 'of_the_month', 'suggested', 'release_at']

class ActionSerializer(serializers.ModelSerializer):
    causes = CauseSerializer(many=True)
    is_completed = serializers.SerializerMethodField()

    def get_is_completed(self, obj: Action) -> bool:
        user = get_user_from_context(self.context)
        if user is None:
            return False
        return obj.is_completed(user.pk)

    class Meta:
        # TODO Completed
        model = Action
        fields = '__all__'

class CampaignSerializer(serializers.ModelSerializer):
    causes = CauseSerializer(many=True)
    learning_resources = LearningResourceSerializer(many=True)
    actions = ListActionSerializer(many=True)
    is_completed = serializers.SerializerMethodField()
    header_image = ImageSerializer()

    def get_is_completed(self, obj: Campaign) -> bool:
        user = get_user_from_context(self.context)
        if user is None:
            return False
        return obj.cached_is_complete(user.pk)

    class Meta:
        model = Campaign
        fields = '__all__'

class NewsArticleSerializer(serializers.ModelSerializer):
    header_image = ImageSerializer()

    class Meta:
        model = NewsArticle
        fields = '__all__'


class OrganisationExtraLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationExtraLink
        fields = ['title', 'link']

class OrganisationSerializer(serializers.ModelSerializer):
    logo = ImageSerializer()
    extra_links = OrganisationExtraLinkSerializer(many=True)

    class Meta:
        model = Organisation
        fields = '__all__'

class CauseIdsSerializer():
    serializers.PrimaryKeyRelatedField(queryset=Cause.objects.all())
