from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from air_service.models import (
    Airport,
    Country,
    City,
    Crew,
    Airplane,
    AirplaneType,
    Route,
    Flight,
    Ticket,
    Order
)

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = [
            "id",
            "name"
        ]

class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city"
        ]

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "country"
        ]

class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name"
        ]

class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = [
            "id",
            "name"
        ]

class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type"
        ]

class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "destination",
            "distance"
        ]

class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time"
        ]

class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
            "order"
        ]

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "user"
        ]
