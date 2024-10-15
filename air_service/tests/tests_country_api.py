from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Country
from air_service.serializers import (
    CountrySerializer,
    CountryRetrieveSerializer
)

COUNTRY_URL = reverse("air-service:country-list")


def detail_url(country_id):
    return reverse("air-service:country-detail", args=(str(country_id),))


def sample_country(**params) -> Country:
    defaults = {
        "name": "Test_country_name"
    }
    defaults.update(params)
    return Country.objects.create(**defaults)


class UnauthenticatedCountryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(COUNTRY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCountryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_country_list(self):
        [sample_country(name=f"test{i}") for i in range(5)]

        res = self.client.get(COUNTRY_URL)
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_country_list_paginated(self):
        [sample_country(name=f"test{i}") for i in range(40)]

        res = self.client.get(COUNTRY_URL, {"page": 2})
        countries = Country.objects.order_by("id")[30:40]
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_countries_by_name(self):
        [sample_country(name=f"test{i + 1}") for i in range(5)]
        sample_country(name="filtered")
        sample_country(name="filtered2")

        res = self.client.get(
            COUNTRY_URL,
            {"country_name": "filtered"}
        )
        incorrect_country = Country.objects.filter(name__exact="test0")
        filtered_countries = Country.objects.filter(name__icontains="filtered")
        serializer_correct_filter = CountrySerializer(
            filtered_countries,
            many=True
        )
        serializer_incorrect_filter = CountrySerializer(
            incorrect_country,
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

    def test_order_countries_by_name(self):
        [sample_country(name=f"test{i + 1}") for i in range(8)]

        res = self.client.get(
            COUNTRY_URL,
            {"ordering": "-name"}
        )
        res_another_ordering = self.client.get(
            COUNTRY_URL,
            {"ordering": "name"}
        )

        ordered_countries = Country.objects.order_by("-name")
        serializer = CountrySerializer(ordered_countries, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertNotEqual(
            res_another_ordering.data["results"],
            serializer.data
        )

    def test_retrieve_country_detail(self):
        country = sample_country()

        url = detail_url(country.id)
        res = self.client.get(url)

        serializer = CountryRetrieveSerializer(country)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_country_forbidden(self):
        payload = {
            "name": "THE USA USA USA"
        }

        res = self.client.post(COUNTRY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_country(self):
        payload = {
            "name": "America"
        }

        res = self.client.post(COUNTRY_URL, payload)
        country = Country.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(country, key))

    def test_update_country(self):
        country = sample_country()
        payload = {
            "name": "Americaaa"
        }

        url = detail_url(country.id)

        res = self.client.patch(url, payload)
        country.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(payload["name"], res.data["name"])

    def test_delete_country(self):
        country = sample_country()

        url = detail_url(country.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
