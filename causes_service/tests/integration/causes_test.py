import pytest

from tests.factories.cause import CauseFactory, CampaignFactory, ActionFactory, LearningResourceFactory, NewsArticleFactory
from causes.models import Campaign, Action, LearningResource

pytestmark = pytest.mark.django_db

def test_list_causes(client):
    CauseFactory()
    response = client.get('/causes/')

    assert response.status_code == 200

def test_get_cause(client):
    cause = CauseFactory()
    response = client.get(f'/causes/{cause.pk}/')

    assert response.status_code == 200
    assert response.data['id'] == cause.pk
    assert response.data['title'] == cause.title

def test_complete_learning_resource(auth_client):
    learning_resources = LearningResourceFactory.create()

    response = auth_client.get(f'/learning_resources/{learning_resources.pk}/')
    assert response.data['is_completed'] is False

    response = auth_client.post(f'/learning_resources/{learning_resources.pk}/complete/')
    assert response.status_code == 200

    response = auth_client.get(f'/learning_resources/{learning_resources.pk}/')
    assert response.data['is_completed'] is True

def test_complete_learning_resource_fails_if_not_authenticated(auth_client):
    auth_client.logout()
    learning_resources = LearningResourceFactory.create()

    response = auth_client.post(f'/learning_resources/{learning_resources.pk}/complete/')
    assert response.status_code == 401

    response = auth_client.get(f'/learning_resources/{learning_resources.pk}/')
    assert response.data['is_completed'] is False

def test_complete_action(auth_client):
    action = ActionFactory.create()

    response = auth_client.get(f'/actions/{action.pk}/')
    assert response.data['is_completed'] is False

    response = auth_client.post(f'/actions/{action.pk}/complete/')
    assert response.status_code == 200

    response = auth_client.get(f'/actions/{action.pk}/')
    assert response.data['is_completed'] is True

def test_complete_action_fails_if_not_authenticated(auth_client):
    auth_client.logout()
    action = ActionFactory.create()

    response = auth_client.post(f'/actions/{action.pk}/complete/')
    assert response.status_code == 401

    response = auth_client.get(f'/actions/{action.pk}/')
    assert response.data['is_completed'] is False

def test_complete_news_article(auth_client):
    article = NewsArticleFactory.create()

    response = auth_client.get(f'/news_articles/{article.pk}/')
    assert response.data['is_completed'] is False

    response = auth_client.post(f'/news_articles/{article.pk}/complete/')
    assert response.status_code == 200

    response = auth_client.get(f'/news_articles/{article.pk}/')
    assert response.data['is_completed'] is True

def test_complete_news_article_fails_if_not_authenticated(auth_client):
    auth_client.logout()
    article = NewsArticleFactory.create()

    response = auth_client.get(f'/news_articles/{article.pk}/')
    assert response.data['is_completed'] is False

    response = auth_client.post(f'/news_articles/{article.pk}/complete/')
    assert response.status_code == 401

    response = auth_client.get(f'/news_articles/{article.pk}/')
    assert response.data['is_completed'] is False

def test_complete_campaign(auth_client):

    learning_resources = LearningResourceFactory.create_batch(2)
    actions = ActionFactory.create_batch(2)
    campaign = CampaignFactory(learning_resources=learning_resources, actions=actions)

    def get_campaign_is_complete() -> bool:
        response = auth_client.get(f'/campaigns/{campaign.pk}/')
        return response.data['is_completed']

    # Is not completed when no resource are completed
    assert get_campaign_is_complete() is False

    for action in actions:
        action.complete(auth_client.user.pk)
    learning_resources[0].complete(auth_client.user.pk)

    # Is not completed when some resource are completed
    assert get_campaign_is_complete() is False

    learning_resources[1].complete(auth_client.user.pk)

    # Is complete when all resources are completed
    assert get_campaign_is_complete() is True

    actions[0].uncomplete(auth_client.user.pk)

    # Is complete after uncompleting action
    assert get_campaign_is_complete() is False

    actions[0].complete(auth_client.user.pk)

    # Is complete after recompleting that action
    assert get_campaign_is_complete() is True

def test_delete_campaign():
    learning_resources = LearningResourceFactory.create_batch(2)
    actions = ActionFactory.create_batch(2)

    ActionFactory.create_batch(1)
    LearningResourceFactory.create_batch(1)

    campaign = CampaignFactory(learning_resources=learning_resources, actions=actions)

    assert Campaign.objects.count() == 1
    assert Action.objects.count() == 3
    assert LearningResource.objects.count() == 3

    campaign.delete()

    assert Campaign.objects.count() == 0
    assert Action.objects.count() == 3
    assert LearningResource.objects.count() == 3
