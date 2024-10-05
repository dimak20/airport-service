from django.urls import path, include
from rest_framework.routers import DefaultRouter

from air_service.views import CountryViewSet, CityViewSet, CrewViewSet, AirplaneViewSet, AirportViewSet, RouteViewSet, \
    FlightViewSet, TicketViewSet, OrderViewSet, AirplaneTypeViewSet, add_view

app_name = "air-service"

router = DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("crew", CrewViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("tickets", TicketViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("celery_test/", add_view, name="celery-test")
]
