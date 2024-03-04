from typing import Generic, TypeVar

import factory
import factory.fuzzy

from causes.models import Cause, Action, LearningResource, Campaign, NewsArticle
from images.models import Image

T = TypeVar('T')

class BaseMetaFactory(Generic[T], factory.base.FactoryMetaClass):
    def __call__(cls, *args, **kwargs) -> T:
        return super().__call__(*args, **kwargs)

class ImageFactory(factory.django.DjangoModelFactory):
    image = factory.Faker("image_url")

    class Meta:
        model = Image

class CauseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cause

    title = factory.Faker("sentence")
    icon = factory.fuzzy.FuzzyChoice(Cause.Icon.values)
    description = factory.Faker("sentence")
    header_image = factory.SubFactory(ImageFactory)

class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Action

    title = factory.Faker("sentence")
    link = factory.Faker("url")
    action_type = factory.fuzzy.FuzzyChoice(Action.Type.values)
    what_description = factory.Faker("sentence")
    why_description = factory.Faker("sentence")
    time = factory.Faker("random_int")
    of_the_month = factory.Faker("boolean")
    suggested = factory.Faker("boolean")

    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    release_at = factory.Faker("past_datetime")

class LearningResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LearningResource

    title = factory.Faker("sentence")
    time = factory.Faker("random_int")
    link = factory.Faker("url")
    learning_resource_type = factory.fuzzy.FuzzyChoice(LearningResource.Type.values)
    source = factory.Faker("sentence")
    release_at = factory.Faker("past_datetime")

class NewsArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsArticle

    title = factory.Faker("sentence")
    subtitle = factory.Faker("sentence")
    source = factory.Faker("sentence")
    link = factory.Faker("url")
    header_image = factory.SubFactory(ImageFactory)
    published_at = factory.Faker("past_datetime")
    release_at = factory.Faker("past_datetime")

class CampaignFactory(factory.django.DjangoModelFactory, metaclass=BaseMetaFactory[Campaign]):
    class Meta:
        model = Campaign

    title = factory.Faker("sentence")
    short_name = factory.Faker("word")
    description = factory.Faker("sentence")
    header_image = factory.SubFactory(ImageFactory)
    of_the_month = factory.Faker("boolean")
    suggested = factory.Faker("boolean")
    release_at = factory.Faker("past_datetime")

    @factory.post_generation
    def actions(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.actions.add(*extracted)

    @factory.post_generation
    def learning_resources(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.learning_resources.add(*extracted)
