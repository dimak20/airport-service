from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Country, City
from air_service.serializers import (
    CityListSerializer,
    CityRetrieveSerializer
)

CITY_URL = reverse("air-service:city-list")


def detail_url(city_id):
    return reverse("air-service:city-detail", args=(str(city_id),))


class UnauthenticatedCityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CITY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCityApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.COUNTRY_SAMPLE = Country.objects.create(name="sample_name")

    def sample_city(self, **params) -> City:
        defaults = {
            "name": "Test_city_name",
            "country": self.COUNTRY_SAMPLE
        }
        defaults.update(params)
        return City.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_city_list(self):
        [self.sample_city(name=f"test{i}") for i in range(5)]

        res = self.client.get(CITY_URL)
        cities = City.objects.all()
        serializer = CityListSerializer(cities, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_city_list_paginated(self):
        [self.sample_city(name=f"{i}") for i in range(40)]

        res = self.client.get(CITY_URL, {"page": 2})
        cities = City.objects.all().order_by("id")[30:]
        serializer = CityListSerializer(cities, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_cities_by_name(self):
        [self.sample_city(name=f"test{i + 1}") for i in range(5)]
        self.sample_city(name="filtered")
        self.sample_city(name="filtered2")

        res = self.client.get(
            CITY_URL,
            {"city_name": "filtered"}
        )
        incorrect_city = City.objects.filter(name__exact="test0")
        filtered_cities = City.objects.filter(name__icontains="filtered")
        serializer_correct_filter = CityListSerializer(
            filtered_cities,
            many=True
        )
        serializer_incorrect_filter = CityListSerializer(
            incorrect_city,
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

    def test_order_cities_by_name(self):
        [self.sample_city(name=f"test{i + 1}") for i in range(8)]

        res = self.client.get(
            CITY_URL,
            {"ordering": "-name"}
        )
        res_another_ordering = self.client.get(
            CITY_URL,
            {"ordering": "name"}
        )

        ordered_cities = City.objects.order_by("-name")
        serializer = CityListSerializer(ordered_cities, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertNotEqual(
            res_another_ordering.data["results"],
            serializer.data
        )

    def test_retrieve_city_detail(self):
        city = self.sample_city()

        url = detail_url(city.id)
        res = self.client.get(url)

        serializer = CityRetrieveSerializer(city)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_city_forbidden(self):
        payload = {
            "name": "Washington"
        }

        res = self.client.post(CITY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCityTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.COUNTRY_SAMPLE = Country.objects.create(name="sample_name")

    def sample_city(self, **params) -> City:
        defaults = {
            "name": "Test_city_name",
            "country": self.COUNTRY_SAMPLE
        }
        defaults.update(params)
        return City.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_city(self):
        payload = {
            "name": "Chicago",
            "country": self.COUNTRY_SAMPLE.id
        }

        res = self.client.post(CITY_URL, payload)
        city = City.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data["name"], city.name)
        self.assertEqual(res.data["country"], self.COUNTRY_SAMPLE.id)

    def test_update_city(self):
        city = self.sample_city()
        payload = {
            "name": "America city"
        }

        url = detail_url(city.id)

        res = self.client.patch(url, payload)
        city.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(payload["name"], res.data["name"])

    def test_delete_city(self):
        city = self.sample_city()

        url = detail_url(city.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
