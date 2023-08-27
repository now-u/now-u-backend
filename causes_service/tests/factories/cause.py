import factory
import factory.fuzzy

from causes.models import Cause, Action
from images.models import Image

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
    title = factory.Faker("sentence")
    link = factory.Faker("url")
    action_type = factory.fuzzy.FuzzyChoice(Action.Type.choices)
    what_description = factory.Faker("sentence")
    why_description = factory.Faker("sentence")
    time = factory.Faker("number")
    of_the_month = factory.Faker("boolean")
    suggested = factory.Faker("boolean")

    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
