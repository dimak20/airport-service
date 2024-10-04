from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Airport, Country, City
from air_service.serializers import (
    AirportListSerializer,
    AirportRetrieveSerializer
)

AIRPORT_URL = reverse("air-service:airport-list")


def detail_url(airport_id):
    return reverse("air-service:airport-detail", args=(str(airport_id),))


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="America")
        cls.city = City.objects.create(
            name="Smaller America",
            country=cls.country
        )

    def sample_airport(self, **params) -> Airport:
        defaults = {
            "name": "default_name",
            "closest_big_city": self.city,
        }
        defaults.update(params)
        return Airport.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_airport_list(self):
        [self.sample_airport() for _ in range(5)]

        res = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_airport_list_paginated(self):
        [self.sample_airport() for _ in range(40)]

        res = self.client.get(AIRPORT_URL, {"page": 2})
        airports = Airport.objects.all()[30:]
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_airports_by_name(self):
        [self.sample_airport(name="test_test") for _ in range(5)]
        self.sample_airport(name="America_airport")
        self.sample_airport(name="airport")

        res = self.client.get(
            AIRPORT_URL,
            {"search_name": "airport"}
        )
        incorrect_airports = Airport.objects.filter(name="airport")
        filtered_airports = Airport.objects.filter(
            name__icontains="airport"
        )
        serializer_correct_filter = AirportListSerializer(
            filtered_airports,
            many=True
        )
        serializer_incorrect_filter = AirportListSerializer(
            incorrect_airports,
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

    def test_filter_airports_by_closest_city_name(self):
        city_1 = City.objects.create(name="find_this", country=self.country)
        [self.sample_airport(name="test_test") for _ in range(5)]
        self.sample_airport(closest_big_city=city_1)
        self.sample_airport(closest_big_city=self.city)

        res = self.client.get(
            AIRPORT_URL,
            {"closest_city_name": "this"}
        )
        incorrect_airports = Airport.objects.filter(
            closest_big_city__name="find"
        )
        filtered_airports = Airport.objects.filter(
            closest_big_city__name__icontains="this"
        )
        serializer_correct_filter = AirportListSerializer(
            filtered_airports,
            many=True
        )
        serializer_incorrect_filter = AirportListSerializer(
            incorrect_airports,
            many=True
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            serializer_correct_filter.data,
            res.data["results"]
        )
        self.assertNotEqual(
            serializer_incorrect_filter.data,
            res.data["results"]
        )

    def test_retrieve_airport_detail(self):
        airport = self.sample_airport()

        url = detail_url(airport.id)
        res = self.client.get(url)

        serializer = AirportRetrieveSerializer(airport)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "default_name",
            "closest_big_city": self.city,
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="America")
        cls.city = City.objects.create(
            name="Smaller America",
            country=cls.country
        )

    def sample_airport(self, **params) -> Airport:
        defaults = {
            "name": "default_name",
            "closest_big_city": self.city,
        }
        defaults.update(params)
        return Airport.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airport(self):
        payload = {
            "name": "default_name_test_123",
            "closest_big_city": self.city.id,
        }

        res = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "closest_big_city":
                self.assertEqual(payload[key], getattr(airport, key).id)
                continue
            self.assertEqual(payload[key], getattr(airport, key))

    def test_update_airport(self):
        airport = self.sample_airport()
        payload = {
            "name": "America airport"
        }

        url = detail_url(airport.id)

        res = self.client.patch(url, payload)
        airport.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(payload["name"], res.data["name"])

    def test_delete_airport(self):
        route = self.sample_airport()

        url = detail_url(route.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
