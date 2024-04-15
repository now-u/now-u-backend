import factory
import factory.fuzzy

from users.models import User

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Faker("email")
    name = factory.Faker("name")
    auth_id = factory.Faker("uuid4")
