from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
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


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "country"
        ]

class CityListSerializer(CitySerializer):
    country = SlugRelatedField(
        slug_field="name",
        many=False,
        read_only=True
    )

class CityRetrieveSerializer(serializers.ModelSerializer):
    country = SlugRelatedField(
        slug_field="name",
        many=False,
        read_only=True
    )
    airports = SlugRelatedField(
        slug_field="name",
        many=True,
        read_only=True
    )
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "country",
            "airports"
        ]


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city"
        ]


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field="name"
    )


class AirportRetrieveSerializer(AirportListSerializer):
    country = serializers.CharField(
        source="closest_big_city.country.name",
        read_only=True
    )
    same_city_airports = serializers.SerializerMethodField()

    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city",
            "country",
            "same_city_airports"
        ]

    def get_same_city_airports(self, obj):
        return [
            airport.name for airport in Airport.objects.filter(
            closest_big_city=obj.id
        ).exclude(id=obj.id)
        ]


class CountryRetrieveSerializer(serializers.ModelSerializer):
    cities = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        read_only=True
    )
    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "cities"
        ]



class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = [
            "id",
            "first_name",
            "last_name"
        ]
class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = [
            "id",
            "full_name"
        ]
class CrewRetrieveSerializer(serializers.ModelSerializer):
    airplanes = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    class Meta:
        model = Crew
        fields = [
            "id",
            "first_name",
            "last_name",
            "airplanes"
        ]

class AirplaneTypeSerializer(serializers.ModelSerializer):
    airplane_park = serializers.IntegerField(read_only=True)
    class Meta:
        model = AirplaneType
        fields = [
            "id",
            "name",
            "airplane_park"
        ]


class AirplaneTypeRetrieveSerializer(AirplaneTypeSerializer):
    airplanes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    class Meta:
        model = AirplaneType
        fields = [
            "id",
            "name",
            "airplane_park",
            "airplanes"
        ]


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "capacity",
            "airplane_type",
            "crew"
        ]


class AirplaneListSerializer(AirplaneSerializer):
    crew = serializers.SlugRelatedField(
        slug_field="full_name",
        read_only=True,
        many=True
    )
    airplane_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        many=False
    )

class AirplaneRetrieveSerializer(AirplaneListSerializer):
    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "crew"
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
