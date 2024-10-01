from django.shortcuts import render
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
    CrewRetrieveSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    model = Country
    queryset = Country.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CountryRetrieveSerializer
        return CountrySerializer

class CityViewSet(viewsets.ModelViewSet):
    model = City
    queryset = City.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer
        if self.action == "retrieve":
            return CityRetrieveSerializer
        return CitySerializer

class CrewViewSet(viewsets.ModelViewSet):
    model = Crew
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        if self.action == "retrieve":
            return CrewRetrieveSerializer
        return CrewSerializer

class AirplaneTypeViewSet(viewsets.ModelViewSet):
    model = AirplaneType
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()

class AirportViewSet(viewsets.ModelViewSet):
    model = Airport
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()

class AirplaneViewSet(viewsets.ModelViewSet):
    model = Airplane
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.all()

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



























