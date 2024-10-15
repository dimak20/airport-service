from datetime import timedelta, timezone as dt_timezone, datetime
import pytz
from django.contrib.auth import get_user_model
from django.db.models import F, Count, QuerySet
from django.db.models.functions import TruncHour
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import (
    Airport,
    Country,
    City,
    Route,
    AirplaneType,
    Airplane,
    Flight
)
from air_service.serializers import (
    FlightRetrieveSerializer,
    FlightListSerializer
)

FLIGHT_URL = reverse("air-service:flight-list")


def detail_url(flight_id):
    return reverse("air-service:flight-detail", args=(str(flight_id),))


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="America")
        cls.city = City.objects.create(name="Smaller America", country=cls.country)
        cls.airport = Airport.objects.create(
            name="Way smaller America",
            closest_big_city=cls.city
        )
        cls.route = Route.objects.create(
            source=cls.airport,
            destination=cls.airport,
            distance=1000
        )
        cls.airplane_type = AirplaneType.objects.create(
            name="some_test_name"
        )
        cls.airplane = Airplane.objects.create(
            name="ordinary_name",
            rows=30,
            seats_in_row=30,
            airplane_type=cls.airplane_type,
        )

    def sample_flight(self, **params) -> Flight:
        defaults = {
            "route": self.route,
            "airplane": self.airplane,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() + timedelta(days=1)

        }
        defaults.update(params)
        return Flight.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def annotate_flights(self) -> QuerySet:
        return Flight.objects.all().annotate(
            tickets_available=
            F("airplane__rows") * F("airplane__seats_in_row")
            - Count("tickets")
        )

    def test_flight_list(self):
        [self.sample_flight() for _ in range(5)]

        res = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all().order_by("pk").annotate(
            tickets_available=
            F("airplane__rows") * F("airplane__seats_in_row")
            - Count("tickets")
        )
        serializer = FlightListSerializer(flights, many=True)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_flight_list_paginated(self):
        [self.sample_flight() for _ in range(40)]

        res = self.client.get(FLIGHT_URL, {"page": 2})
        flights = self.annotate_flights().order_by("id")[30:40]
        serializer = FlightListSerializer(flights, many=True)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_flights_by_name(self):
        route = Route.objects.create(
            source=self.airport,
            destination=self.airport,
            distance=900
        )
        route_2 = Route.objects.create(
            source=self.airport,
            destination=self.airport,
            distance=900
        )
        [self.sample_flight() for _ in range(5)]
        self.sample_flight(route=route)
        self.sample_flight(route=route_2)

        res = self.client.get(
            FLIGHT_URL,
            {"route_ids": f"{route.id},{route_2.id}"}
        )
        incorrect_flights = Flight.objects.filter(
            route__id__in=[self.route.id]
        ).annotate(
            tickets_available=
            F("airplane__rows")
            * F("airplane__seats_in_row")
            - Count("tickets")
        )
        filtered_flights = Flight.objects.filter(
            route__id__in=[route.id, route_2.id]
        ).annotate(
            tickets_available=
            F("airplane__rows")
            * F("airplane__seats_in_row")
            - Count("tickets")
        )
        serializer_correct_filter = FlightListSerializer(
            filtered_flights,
            many=True
        )
        serializer_incorrect_filter = FlightListSerializer(
            incorrect_flights,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            serializer_correct_filter.data,
            res.data["results"]
        )
        self.assertNotEqual(
            serializer_incorrect_filter.data,
            res.data["results"]
        )

    def test_filter_flights_by_airplane_name(self):
        airplane = Airplane.objects.create(
            name="new name",
            rows=123,
            seats_in_row=456,
            airplane_type=self.airplane_type
        )
        [self.sample_flight() for _ in range(2)]
        self.sample_flight(airplane=airplane)
        self.sample_flight(airplane=airplane)

        res = self.client.get(
            FLIGHT_URL,
            {"airplane_name": "new"}
        )
        incorrect_flights = Flight.objects.filter(
            airplane__name__icontains=""
        ).annotate(
            tickets_available=
            F("airplane__rows")
            * F("airplane__seats_in_row")
            - Count("tickets")
        ).order_by("id")
        filtered_flights = Flight.objects.filter(
            airplane__name__icontains="new"
        ).annotate(
            tickets_available=
            F("airplane__rows")
            * F("airplane__seats_in_row")
            - Count("tickets")
        ).order_by("id")
        serializer_correct_filter = FlightListSerializer(
            filtered_flights,
            many=True
        )
        serializer_incorrect_filter = FlightListSerializer(
            incorrect_flights,
            many=True
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            serializer_correct_filter.data,
            res.data["results"]
        )
        self.assertNotEqual(
            serializer_incorrect_filter.data,
            res.data["results"]
        )

    def test_filter_flights_by_departure_time_hour(self):
        delta = timezone.now() + timedelta(hours=1)
        [self.sample_flight() for _ in range(5)]
        self.sample_flight(departure_time=delta)
        self.sample_flight(
            departure_time=delta + timedelta(minutes=5)
        )

        res = self.client.get(
            FLIGHT_URL,
            {"departure_time_hour": delta}
        )
        incorrect_flights = self.annotate_flights().annotate(
            departure_hour=TruncHour("departure_time")
        ).filter(
            departure_hour=timezone.now()
        )

        filtered_flights = self.annotate_flights().annotate(
            departure_hour=TruncHour("departure_time")
        ).filter(
            departure_hour=delta
        )

        serializer_correct_filter = FlightListSerializer(
            filtered_flights,
            many=True
        )
        serializer_incorrect_filter = FlightListSerializer(
            incorrect_flights,
            many=True
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            serializer_correct_filter.data,
            res.data["results"]
        )
        self.assertNotIn(
            serializer_incorrect_filter.data,
            res.data["results"]
        )

    def test_filter_flights_by_departure_time_hour_after(self):
        delta = timezone.now() + timedelta(minutes=5)
        [self.sample_flight() for _ in range(5)]
        self.sample_flight(departure_time=delta)
        self.sample_flight(
            departure_time=delta + timedelta(minutes=5)
        )

        res = self.client.get(
            FLIGHT_URL,
            {"departure_time_hour_after": delta}
        )
        incorrect_flights = self.annotate_flights().annotate(
            departure_hour=TruncHour("departure_time")
        ).filter(
            departure_hour=timezone.now()
        ).order_by("id")

        filtered_flights = self.annotate_flights().annotate(
            departure_hour=TruncHour("departure_time")
        ).filter(
            departure_hour__gte=delta
        ).order_by("id")

        serializer_correct_filter = FlightListSerializer(
            filtered_flights,
            many=True
        )
        serializer_incorrect_filter = FlightListSerializer(
            incorrect_flights,
            many=True
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            serializer_correct_filter.data,
            res.data["results"]
        )
        self.assertNotIn(
            serializer_incorrect_filter.data,
            res.data["results"]
        )

    def test_filter_flights_by_departure_time_hour_before(self):
        delta = timezone.now() - timedelta(hours=2)
        [self.sample_flight() for _ in range(5)]
        self.sample_flight(departure_time=delta)
        self.sample_flight(departure_time=delta + timedelta(minutes=3))

        res = self.client.get(
            FLIGHT_URL,
            {"departure_time_hour_before": delta}
        )

        incorrect_flights = self.annotate_flights().annotate(
            departure_hour=TruncHour("departure_time")
        ).filter(
            departure_hour__gt=delta
        ).order_by("id")

        filtered_flights = self.annotate_flights().annotate(
            departure_hour=TruncHour("departure_time")
        ).filter(
            departure_hour__lte=delta
        ).order_by("id")

        serializer_correct_filter = FlightListSerializer(
            filtered_flights,
            many=True
        )
        serializer_incorrect_filter = FlightListSerializer(
            incorrect_flights,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            serializer_correct_filter.data,
            res.data["results"]
        )
        self.assertNotIn(
            serializer_incorrect_filter.data,
            res.data["results"]
        )

    def test_retrieve_flight_detail(self):
        flight = self.sample_flight()
        flight_query = self.annotate_flights().first()
        url = detail_url(flight.id)
        res = self.client.get(url)

        serializer = FlightRetrieveSerializer(flight_query)

        self.assertEqual(list(res.data), list(serializer.data))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_flight_forbidden(self):
        payload = {
            "route": self.route,
            "airplane": self.airplane,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() + timedelta(days=1)

        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="America")
        cls.city = City.objects.create(name="Smaller America", country=cls.country)
        cls.airport = Airport.objects.create(
            name="Way smaller America",
            closest_big_city=cls.city
        )
        cls.route = Route.objects.create(
            source=cls.airport,
            destination=cls.airport,
            distance=1000
        )
        cls.airplane_type = AirplaneType.objects.create(
            name="some_test_name"
        )
        cls.airplane = Airplane.objects.create(
            name="ordinary_name",
            rows=30,
            seats_in_row=30,
            airplane_type=cls.airplane_type,
        )

    def sample_flight(self, **params) -> Flight:
        defaults = {
            "route": self.route,
            "airplane": self.airplane,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() + timedelta(days=1)

        }
        defaults.update(params)
        return Flight.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight_correct_data(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() + timedelta(days=1)

        }

        res = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.filter(pk=res.data["id"]).annotate(
            tickets_available=
            F("airplane__rows") * F("airplane__seats_in_row")
            - Count("tickets")
        ).first()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "route" or key == "airplane":
                self.assertEqual(payload[key], getattr(flight, key).id)
                continue
            self.assertEqual(payload[key], getattr(flight, key))

    def test_update_flight(self):
        flight = self.sample_flight()
        payload = {
            "departure_time": timezone.now() + timedelta(days=1),
            "arrival_time": timezone.now() + timedelta(days=3)
        }

        url = detail_url(flight.id)

        res = self.client.patch(url, payload)
        flight.refresh_from_db()


        expected_arrival_time = payload["arrival_time"].astimezone(dt_timezone.utc)
        res_arrival_time = datetime.fromisoformat(res.data["arrival_time"].replace("Z", "+00:00")).astimezone(dt_timezone.utc)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_arrival_time, res_arrival_time)

    def test_create_flight_incorrect_data(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() - timedelta(days=1)

        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_flight(self):
        route = self.sample_flight()

        url = detail_url(route.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
