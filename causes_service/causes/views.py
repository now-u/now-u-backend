from django.utils import timezone
from typing import Any
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from .models import Cause, LearningResource, Action, Campaign, NewsArticle, Organisation
from .serializers import CauseSerializer, LearningResourceSerializer, ActionSerializer, CampaignSerializer, ListCampaignSerializer, ListActionSerializer, NewsArticleSerializer, OrganisationSerializer, CauseIdsSerializer

class CauseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cause.objects.all()
    serializer_class = CauseSerializer
    pagination_class = None

    # TODO Make bulk
    @extend_schema("causes_select", request=CauseIdsSerializer)
    @action(detail=False, methods=['post'])
    def select(self, request, pk=None) -> Response:
        action: Cause = self.get_object()
        action.select(request.user.id)
        return Response({'status': 'ok'})

class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    # TODO Move this to get_query because idk when datetime.now is called!
    queryset = Action.objects.filter_unreleased(is_active_at=timezone.now())

    def get_serializer_class(self):
        if self.action == 'list':
            return ListActionSerializer
        return ActionSerializer

    # TODO Handle correct response rather than just None
    @extend_schema(operation_id="actions_complete", request=None, responses=None)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None) -> Response:
        action: Action = self.get_object()
        action.complete(request.user.id)
        # TODO Return type is wrong in smithy (it things itll get an action back) - maybe that makes sense?
        return Response({'status': 'ok'})

    @extend_schema(operation_id="actions_uncomplete", request=None, responses=None)
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def uncomplete(self, request, pk=None) -> Response:
        action: Action = self.get_object()
        action.uncomplete(request.user.id)
        return Response({'status': 'ok'})

class LearningResourceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LearningResourceSerializer

    def get_queryset(self) -> QuerySet[Any]:
        # Check if dev mode and staff user
        user = self.request.user
        # TODO Try and fix these types
        if (user is not None and user.is_staff):
            return LearningResource.objects.all()
        return LearningResource.objects.filter_unreleased(is_active_at=timezone.now())

    @extend_schema(operation_id="learning_resources_complete", request=None, responses=None)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None) -> Response:
        # TODO Handle duplicates
        learning_resource: LearningResource = self.get_object()
        learning_resource.complete(request.user.id)
        return Response({'status': 'ok'})

class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter_unreleased(is_active_at=timezone.now())

    def get_serializer_class(self):
        if self.action == 'list':
            return ListCampaignSerializer
        return CampaignSerializer

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NewsArticleSerializer

    def get_queryset(self) -> QuerySet[NewsArticle]:
        return NewsArticle.objects.filter_unreleased(is_active_at=timezone.now())

    @extend_schema(operation_id="news_article_complete", request=None, responses=None)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None) -> Response:
        # TODO Handle duplicates
        news_article: NewsArticle = self.get_object()
        news_article.complete(request.user.id)
        return Response({'status': 'ok'})

class OrganisationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer


class SelectCausesViewSet(viewsets.ViewSet):
    def update(self, request):
        serializer = CauseIdsSerializer(data=request.data)
        return Response(serializer.data)

