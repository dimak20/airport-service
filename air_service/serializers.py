from typing import Any

from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

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

    def get_same_city_airports(self, obj) -> list[str]:
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
            "image"
        ]


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        many=False
    )


class AirplaneRetrieveSerializer(AirplaneListSerializer):
    crew = serializers.SlugRelatedField(
        slug_field="full_name",
        read_only=True,
        many=True
    )

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "image",
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


class RouteListSerializer(RouteSerializer):
    source = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    def get_source(self, obj) -> str:
        return (
            f"{obj.source.name} "
            f"({obj.source.closest_big_city.name})"
        )

    def get_destination(self, obj) -> str:
        return (
            f"{obj.destination.name} "
            f"({obj.destination.closest_big_city.name})"
        )


class RouteRetrieveSerializer(RouteListSerializer):
    source = serializers.StringRelatedField(
        many=False,
        read_only=True,
    )
    destination = serializers.StringRelatedField(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "destination",
            "distance_in_km",
            "distance_in_nm"
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

    def validate(self, attrs):
        Flight.validate_time(
            attrs["departure_time"],
            attrs["arrival_time"],
            serializers.ValidationError
        )


class FlightListSerializer(FlightSerializer):
    departure_time = serializers.SerializerMethodField()
    arrival_time = serializers.SerializerMethodField()
    route = serializers.StringRelatedField(
        read_only=True,
        many=False
    )
    airplane = serializers.CharField(
        read_only=True,
        source="airplane.name"
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "tickets_available"
        ]

    def get_departure_time(self, obj) -> str:
        return obj.departure_time.strftime("%Y-%m-%d %H:%M")

    def get_arrival_time(self, obj) -> str:
        return obj.arrival_time.strftime("%Y-%m-%d %H:%M")


class FlightRetrieveSerializer(FlightListSerializer):
    route = serializers.SerializerMethodField()
    airplane = serializers.SerializerMethodField()
    tickets = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "flight_time",
            "tickets"
        ]

    def get_route(self, obj) -> str:
        return f"From {obj.route.source} to {obj.route.destination}"

    def get_airplane(self, obj) -> str:
        return f"{obj.airplane.name} ({obj.airplane.airplane_type.name})"

    def get_tickets(self, obj) -> list[dict[str, Any]]:
        return [
            {
                "seat": ticket.seat,
                "row": ticket.row
            }
            for ticket in obj.tickets.all()
        ]


class FlightDetailSerializer(FlightRetrieveSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "flight_time",
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
        ]

    def validate(self, attrs):
        Ticket.validate_seat_row(
            attrs["seat"],
            attrs["row"],
            attrs["flight"].airplane.seats_in_row,
            attrs["flight"].airplane.rows,
            serializers.ValidationError
        )
        return attrs


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightDetailSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "tickets"
        ]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj) -> str:
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")


class OrderRetrieveSerializer(OrderListSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
