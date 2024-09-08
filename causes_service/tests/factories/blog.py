import factory
import factory.fuzzy
import pytz

from .cause import ImageFactory
from .user import UserFactory

from blogs.models import Blog

class BlogFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("sentence")
    subtitle = factory.Faker("sentence")
    slug = factory.Faker("word")

    header_image = factory.SubFactory(ImageFactory)
    reading_time = factory.Faker("random_int")
    body = factory.Faker("sentence")
    authors = factory.List([
        factory.SubFactory(UserFactory)
    ])

    created_at = factory.Faker("date_time", tzinfo=pytz.utc)
    updated_at = factory.Faker("date_time", tzinfo=pytz.utc)
    release_at = factory.Faker("past_datetime", tzinfo=pytz.utc)

    class Meta:
        model = Blog

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            # Simple build, or nothing to add, do nothing.
            return

        authors = extracted or [
            UserFactory()
        ]

        # Add the iterable of groups using bulk addition
        self.authors.add(*authors)
