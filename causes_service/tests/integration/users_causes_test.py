import pytest
from tests.factories.cause import CampaignFactory, CauseFactory, ActionFactory, LearningResourceFactory, NewsArticleFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

def test_get_me(auth_client):
    # TODO Test with completed acitons and campaigns
    response = auth_client.get('/me/causesInfo/')
    assert response.status_code == 200

def test_select_causes(auth_client):
    causes = CauseFactory.create_batch(3)
    response = auth_client.patch('/me/causesInfo/', { 'selected_causes_ids': [causes[0].pk, causes[2].pk] })

    assert response.status_code == 200
    assert response.data['selected_causes_ids'] == [causes[0].pk, causes[2].pk]

def test_causes_user(auth_client):
    user = UserFactory()
    auth_client.set_user(user)

    action = ActionFactory.create()
    ActionFactory.create()
    response = auth_client.post(f'/actions/{action.pk}/complete/')
    assert response.status_code == 200

    NewsArticleFactory.create()
    news_article = NewsArticleFactory.create()
    response = auth_client.post(f'/news_articles/{news_article.pk}/complete/')
    assert response.status_code == 200

    learning_resource = LearningResourceFactory.create()
    campaign = CampaignFactory.create(learning_resources=[learning_resource])

    response = auth_client.post(f'/learning_resources/{learning_resource.pk}/complete/')
    assert response.status_code == 200

    response = auth_client.get('/me/causesInfo/')
    assert response.status_code == 200
    assert list(response.data["completed_action_ids"]) == [action.pk]
    assert list(response.data["completed_news_article_ids"]) == [news_article.pk]
    assert list(response.data["completed_learning_resource_ids"]) == [learning_resource.pk]
    assert list(response.data["completed_campaign_ids"]) == [campaign.pk]
