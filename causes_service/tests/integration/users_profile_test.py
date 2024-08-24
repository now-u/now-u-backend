import pytest
from unittest.mock import MagicMock, patch
from tests.factories.cause import ActionFactory, CampaignFactory, LearningResourceFactory
from causes.models import Campaign, Action, LearningResource
from users.models import User

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
    assert response.data['name'] == new_name

def test_update_me_fails_with_empty_string_name(auth_client):
    response = auth_client.patch('/me/profile/', { 'name': '' })
    assert response.status_code == 400

@patch('users.models.get_supabase_client')
def test_delete_me(mock_get_supabase_client, auth_client):
    mock = MagicMock()
    mock_get_supabase_client.return_value = mock
    mock.auth.admin.delete_user = MagicMock(return_value=None)

    actions = ActionFactory.create_batch(2)
    learning_resources = LearningResourceFactory.create_batch(2)
    CampaignFactory.create(learning_resources=learning_resources[:1])

    response = auth_client.post(f'/actions/{actions[0].pk}/complete/')
    assert response.status_code == 200

    response = auth_client.post(f'/learning_resources/{learning_resources[0].pk}/complete/')

    assert response.status_code == 200
    assert response.data == { "status": "ok" }

    response = auth_client.delete('/me/delete/')
    assert response.status_code == 204

    assert Action.objects.count() == 2 
    assert LearningResource.objects.count() == 2
    assert Campaign.objects.count() == 1

    user = User.objects.get(pk=auth_client.user.pk)
    assert user.name is None
    assert user.email is None
    assert user.auth_id == auth_client.user.auth_id
    assert user.status == User.UserStatus.DELETED
