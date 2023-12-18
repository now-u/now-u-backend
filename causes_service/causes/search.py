from datetime import datetime
from django.db.models.query import QuerySet
import meilisearch
from dataclasses import dataclass
from django.db.models.base import ModelBase
from rest_framework.serializers import SerializerMetaclass
from rest_framework.renderers import JSONRenderer

from causes.models import Action, LearningResource, Campaign, NewsArticle
from causes.serializers import ListActionSerializer, LearningResourceSerializer, ListCampaignSerializer, NewsArticleSerializer

@dataclass
class ModelSearchIndex:
    index_name: str
    searchable_attributes: list[str]
    filterable_attributes: list[str]
    sortable_attributes: list[str]
    model: ModelBase
    serializer: SerializerMetaclass
    # TODO Make sure the queryset matches the type of the model
    queryset: QuerySet

    def populate_search_index(self, client: meilisearch.Client):
        serializer = self.serializer(self.queryset.all(), many=True) # type: ignore
        json = JSONRenderer().render(serializer.data)
        index = client.index(self.index_name)
        index.add_documents(json)

    def create_search_index(self, client: meilisearch.Client):
        client.create_index(self.index_name, { 'primaryKey': 'id' })
        index = client.index(self.index_name)
        index.update_settings({
            'displayedAttributes': ['*'],
            'searchableAttributes': self.searchable_attributes,
            'filterableAttributes': self.filterable_attributes,
            'sortableAttributes': self.sortable_attributes,
        })

    def delete_search_index(self, client: meilisearch.Client):
        client.delete_index(self.index_name)


# TODO On any update to resources, push to search service
# TODO Filter for enabled resources only!
SEARCH_INDICIES = [
    ModelSearchIndex(
        index_name='learning_resources',
        searchable_attributes=['title', 'source'],
        filterable_attributes=['id', 'time', 'source', 'causes.id', 'release_at_timestamp', 'suggested', 'of_the_month'],
        sortable_attributes=['release_at_timestamp'],
        model=LearningResource,
        serializer=LearningResourceSerializer,
        queryset=LearningResource.objects.filter_active(is_active_at=datetime.now()).filter(causes__gte=1)
    ),
    ModelSearchIndex(
        index_name='actions',
        searchable_attributes=['title', 'what_description', 'why_description'],
        filterable_attributes=['id', 'time', 'of_the_month', 'suggested', 'action_type', 'causes.id', 'release_at_timestamp'],
        sortable_attributes=['release_at_timestamp'],
        model=Action,
        serializer=ListActionSerializer,
        queryset=Action.objects.filter_active(is_active_at=datetime.now()).filter(causes__gte=1)
    ),
    ModelSearchIndex(
        index_name='campaigns',
        searchable_attributes=['title', 'short_name', 'description'],
        filterable_attributes=['id', 'of_the_month', 'suggested', 'causes.id', 'release_at_timestamp'],
        sortable_attributes=['release_at_timestamp'],
        model=Campaign,
        serializer=ListCampaignSerializer,
        queryset=Campaign.objects.filter_active(is_active_at=datetime.now()).filter(causes__gte=1)
    ),
    ModelSearchIndex(
        index_name='news_articles',
        searchable_attributes=['title', 'subtitle', 'source',],
        filterable_attributes=['id', 'causes.id', 'release_at_timestamp', 'published_at_timestamp'],
        sortable_attributes=['release_at_timestamp', 'published_at_timestamp'],
        model=NewsArticle,
        serializer=NewsArticleSerializer,
        queryset=NewsArticle.objects.filter_active(is_active_at=datetime.now())
    ),
]
