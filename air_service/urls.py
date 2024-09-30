from django.urls import path, include
from rest_framework.routers import DefaultRouter

from air_service.views import CountryViewSet

app_name = "air_service"

router = DefaultRouter()
router.register("countries", CountryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]