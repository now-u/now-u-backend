import pytest

from tests.factories.blog import BlogFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

def test_get_blog(client):
    authors = [
        UserFactory(
            name="John Doe",
            blog_profile_description="I am an avid blogger",
        ),
        UserFactory(),
    ]

    BlogFactory(id=1, slug="abc", authors=authors)
    response = client.get('/blogs/abc/')

    assert response.status_code == 200
    assert response.data['id'] == 1
    assert len(response.data['authors']) == 2
    assert response.data['authors'][0]['name'] == "John Doe"
    assert response.data['authors'][0]['description'] == "I am an avid blogger"
