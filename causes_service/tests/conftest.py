import pytest
from rest_framework.test import APIClient

from users.models import User
from tests.factories.user import UserFactory

class AuthClient(APIClient):
    _user: User

    def set_user(self, user: User):
        self._user = user
        self.force_authenticate(user=user)

    @property
    def user(self) -> User:
        return self._user


@pytest.fixture
def auth_client():
    client = AuthClient()
    client.set_user(UserFactory())
    return client
