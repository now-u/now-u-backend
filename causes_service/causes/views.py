from datetime import datetime
from typing import Any
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from .models import Cause, LearningResource, Action, Campaign, NewsArticle, Organisation
from .serializers import CauseSerializer, LearningResourceSerializer, ActionSerializer, CampaignSerializer, ListCampaignSerializer, ListActionSerializer, NewsArticleSerializer, OrganisationSerializer, CauseIdsSerializer

class CauseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cause.objects.all()
    serializer_class = CauseSerializer

    # TODO Make bulk
    @extend_schema("causes_select", request=CauseIdsSerializer)
    @action(detail=False, methods=['post'])
    def select(self, request, pk=None) -> Response:
        action: Cause = self.get_object()
        action.select(request.user.id)
        return Response({'status': 'ok'})

class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    # TODO Move this to get_query because idk when datetime.now is called!
    queryset = Action.objects.filter_active(is_active_at=datetime.now())

    def get_serializer_class(self):
        if self.action == 'list':
            return ListActionSerializer
        return ActionSerializer

    # TODO Handle correct response rather than just None
    @extend_schema(operation_id="actions_complete", request=None, responses=None)
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None) -> Response:
        action: Action = self.get_object()
        action.complete(request.user.id)
        # TODO Return type is wrong in smithy (it things itll get an action back) - maybe that makes sense?
        return Response({'status': 'ok'})

    @extend_schema(operation_id="actions_uncomplete", request=None, responses=None)
    @action(detail=True, methods=['delete'])
    def uncomplete(self, request, pk=None) -> Response:
        action: Action = self.get_object()
        action.uncomplete(request.user.id)
        return Response({'status': 'ok'})

class LearningResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LearningResource.objects.filter_active(is_active_at=datetime.now())
    serializer_class = LearningResourceSerializer

    def get_queryset(self) -> QuerySet[Any]:
        # Check if dev mode and staff user
        user = self.request.user
        # TODO Try and fix these types
        if (user is not None and user.is_staff):
            return LearningResource.objects.all()
        return super().get_queryset()

    @extend_schema(operation_id="learning_resources_complete", request=None, responses=None)
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None) -> Response:
        # TODO Handle duplicates
        learningResource: LearningResource = self.get_object()
        learningResource.complete(request.user.id)
        return Response({'status': 'ok'})

class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Campaign.objects.filter_active(is_active_at=datetime.now())

    def get_serializer_class(self):
        if self.action == 'list':
            return ListCampaignSerializer
        return CampaignSerializer

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.filter_active(is_active_at=datetime.now())
    serializer_class = NewsArticleSerializer

class OrganisationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer


class SelectCausesViewSet(viewsets.ViewSet):
    def update(self, request):
        serializer = CauseIdsSerializer(data=request.data)
        return Response(serializer.data)

