import pytest
from tests.factories.cause import CauseFactory

pytestmark = pytest.mark.django_db

def test_get_me(auth_client):
    # TODO Test with completed acitons and campaigns
    response = auth_client.get(f'/me/causesInfo/')
    assert response.status_code == 200

def test_select_causes(auth_client):
    causes = CauseFactory.create_batch(3)
    response = auth_client.patch(f'/me/causesInfo/', { 'selected_causes_ids': [causes[0].pk, causes[2].pk] })

    assert response.status_code == 200
    assert response.data['selected_causes_ids'] == [causes[0].pk, causes[2].pk]
