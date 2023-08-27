import pytest
from django.urls import reverse

from tests.factories.cause import CauseFactory

pytestmark = pytest.mark.django_db

def test_list_causes(client):
    cause = CauseFactory()
    response = client.get('/causes/')

    assert response.status_code == 200

def test_get_cause(client):
    cause = CauseFactory()
    response = client.get(f'/causes/{cause.pk}/')

    assert response.status_code == 200
    assert response.data['id'] == cause.pk
    assert response.data['title'] == cause.title
