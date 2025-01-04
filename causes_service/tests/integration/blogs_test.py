from datetime import timedelta
import pytest

from tests.factories.blog import BlogFactory
from tests.factories.user import UserFactory
from django.utils import timezone

pytestmark = pytest.mark.django_db

def test_get_blog(client):
    authors = [
        UserFactory(
            id = 10,
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
    assert response.data['authors'][0]['id'] == 10
    assert response.data['authors'][0]['name'] == "John Doe"
    assert response.data['authors'][0]['description'] == "I am an avid blogger"

def test_blog_viewset_filtering(client):
    now = timezone.now()
    past_date=now - timedelta(days=5)
    future_date=now + timedelta(days=3)

    #create blogs with release date in the past and future
    BlogFactory(release_at = past_date)
    BlogFactory(release_at = future_date)
     
    #request the blogs API
     
    response = client.get('/blogs/')

    assert response.status_code == 200
    assert len(response.data['results']) == 1 # Only the blog with past_date should be returned
    assert response.data['results'][0]['release_at'] <= now.isoformat() 

def test_blog_viewset_filtering_no_blogs(client):
     now = timezone.now()
     future_date = now + timedelta(days=3)
     #create blog with release date in  future
     BlogFactory(release_at = future_date)

     #request the blogs API
     
     response = client.get('/blogs/')
     assert response.status_code == 200
     assert len(response.data['results']) == 0  # No Blogs should be returned

