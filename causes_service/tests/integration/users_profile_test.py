import pytest


pytestmark = pytest.mark.django_db

def test_get_fails_if_unauthenticated(client):
    response = client.get('/me/profile/')
    assert response.status_code == 401

def test_get_me(auth_client):
    response = auth_client.get('/me/profile/')

    assert response.status_code == 200
    assert response.data['email'] == auth_client.user.email
    assert response.data['name'] == auth_client.user.name

def test_update_me(auth_client):
    new_name = 'new name'
    assert auth_client.user.name != new_name
    response = auth_client.patch('/me/profile/', { 'name': new_name })
    assert response.status_code == 200
    print(response.data)
    assert response.data['name'] == new_name
