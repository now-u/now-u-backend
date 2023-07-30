import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories.user import UserFactory

@pytest.mark.django_db
def test_get_fails_if_unauthenticated(client):
    response = client.get('/me/')
    assert response.status_code == 401

@pytest.mark.django_db
def test_get_me(auth_client):
    response = auth_client.get(f'/me/')

    assert response.status_code == 200
    assert response.data['email'] == auth_client.user.email
    assert response.data['first_name'] == auth_client.user.first_name
    assert response.data['last_name'] == auth_client.user.last_name

@pytest.mark.django_db
def test_update_me(auth_client):
    response = auth_client.patch(f'/me/', body={'first_name': 'new_first_name', 'last_name': 'new_last_name'})

    assert response.status_code == 200
    assert response.data['first_name'] == 'new_first_name'
    assert response.data['last_name'] == 'new_last_name'
