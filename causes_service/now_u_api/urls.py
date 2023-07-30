"""
URL configuration for now_u_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from causes import views as causeViews
from users import views as userViews
import django_saml2_auth.views
from now_u_api import settings

from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

router = routers.DefaultRouter()
router.register(r'actions', causeViews.ActionViewSet)
router.register(r'causes', causeViews.CauseViewSet)
router.register(r'learning_resources', causeViews.LearningResourceViewSet)
router.register(r'campaigns', causeViews.CampaignViewSet)
router.register(r'organisations', causeViews.OrganisationViewSet)
router.register(r'new_articles', causeViews.NewsArticleViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path(r'me/profile', userViews.UserProfileView.as_view()),
    path(r'me/causesInfo', userViews.CausesUserView.as_view()),

    path('api-auth/', include('rest_framework.urls', namespace="rest_framework")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(), name='redoc'),

    re_path(r'^saml2_auth/', include('django_saml2_auth.urls')),
    re_path(r'^admin/login/$', django_saml2_auth.views.signin),
]

# In debug mode we serve static files
if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
