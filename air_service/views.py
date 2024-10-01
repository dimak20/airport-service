from django.db.models import Count
from rest_framework import viewsets

from air_service.models import (
    Country,
    City,
    Crew,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Ticket,
    Order
)
from air_service.serializers import (
    CountrySerializer,
    CitySerializer,
    CrewSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    AirplaneSerializer,
    RouteSerializer,
    FlightSerializer,
    TicketSerializer,
    OrderSerializer, CountryRetrieveSerializer, CityListSerializer, CityRetrieveSerializer, CrewListSerializer,
    CrewRetrieveSerializer, AirplaneTypeRetrieveSerializer, AirportListSerializer, AirportRetrieveSerializer,
    AirplaneListSerializer, AirplaneRetrieveSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    model = Country
    queryset = Country.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CountryRetrieveSerializer

        return CountrySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            return queryset.select_related()

        return queryset


class CityViewSet(viewsets.ModelViewSet):
    model = City
    queryset = City.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer

        if self.action == "retrieve":
            return CityRetrieveSerializer

        return CitySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            return queryset.select_related()

        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    model = Crew
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        if self.action == "retrieve":
            return CrewRetrieveSerializer

        return CrewSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            return queryset.prefetch_related("airplanes")

        return queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    model = AirplaneType
    queryset = AirplaneType.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneTypeRetrieveSerializer

        return AirplaneTypeSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list" or self.action == "retrieve":
            queryset = (
                queryset.
                select_related().
                annotate(
                    airplane_park=Count("airplanes")
                ))

        return queryset.order_by("name")


class AirportViewSet(viewsets.ModelViewSet):
    model = Airport
    queryset = Airport.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        if self.action == "retrieve":
            return AirportRetrieveSerializer

        return AirportSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list" or self.action == "retrieve":
            return queryset.select_related()

        return queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    model = Airplane
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneRetrieveSerializer

        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            return queryset.select_related().prefetch_related("crew")

        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    model = Route
    serializer_class = RouteSerializer
    queryset = Route.objects.all()


class FlightViewSet(viewsets.ModelViewSet):
    model = Flight
    serializer_class = FlightSerializer
    queryset = Flight.objects.all()


class TicketViewSet(viewsets.ModelViewSet):
    model = Ticket
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    model = Order
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
