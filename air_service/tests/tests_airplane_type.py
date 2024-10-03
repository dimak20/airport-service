from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import AirplaneType
from air_service.serializers import (
    AirplaneTypeSerializer,
    AirplaneTypeRetrieveSerializer
)

AIRPLANE_TYPE_URL = reverse("air-service:airplanetype-list")


def detail_url(airplane_type_id):
    return reverse(
        "air-service:airplanetype-detail",
        args=(str(airplane_type_id),)
    )


def sample_airplane_type(**params) -> AirplaneType:
    defaults = {
        "name": "Test_airplane_type_name"
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


class UnauthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_airplane_type_list(self):
        [sample_airplane_type(name=f"test{i}") for i in range(5)]

        res = self.client.get(AIRPLANE_TYPE_URL)
        airplane_types = AirplaneType.objects.annotate(
            airplane_park=Count("airplanes")
        )
        serializer = AirplaneTypeSerializer(
            airplane_types,
            many=True
        )

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_airplane_type_list_paginated(self):
        [sample_airplane_type(name=f"test{i}") for i in range(40)]

        res = self.client.get(AIRPLANE_TYPE_URL, {"page": 2})
        airplane_types = (
            AirplaneType.objects
            .filter(id__in=range(31, 41))
            .annotate(
                airplane_park=Count("airplanes")
            )
        )
        serializer = AirplaneTypeSerializer(airplane_types, many=True)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_airplane_types_by_name(self):
        [sample_airplane_type(name=f"test{i + 1}") for i in range(5)]
        sample_airplane_type(name="filtered")
        sample_airplane_type(name="filtered2")

        res = self.client.get(
            AIRPLANE_TYPE_URL,
            {"search_name": "filtered"}
        )
        incorrect_airplane_types = AirplaneType.objects.filter(
            name__exact="test0"
        ).annotate(
            airplane_park=Count("airplanes")
        )
        filtered_airplane_types = AirplaneType.objects.filter(
            name__icontains="filtered"
        ).annotate(
            airplane_park=Count("airplanes")
        )
        serializer_correct_filter = AirplaneTypeSerializer(
            filtered_airplane_types,
            many=True
        )
        serializer_incorrect_filter = AirplaneTypeSerializer(
            incorrect_airplane_types,
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

    def test_order_airplane_types_by_name(self):
        [sample_airplane_type(name=f"test{i + 1}") for i in range(8)]

        res = self.client.get(
            AIRPLANE_TYPE_URL,
            {"ordering": "-name"}
        )
        res_another_ordering = self.client.get(
            AIRPLANE_TYPE_URL,
            {"ordering": "name"}
        )

        ordered_airplane_types = AirplaneType.objects.annotate(
            airplane_park=Count("airplanes")
        ).order_by("-name")
        serializer = AirplaneTypeSerializer(
            ordered_airplane_types,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertNotEqual(
            res_another_ordering.data["results"],
            serializer.data
        )

    def test_retrieve_airplane_type_detail(self):
        airplane_type = sample_airplane_type()
        airplane_type_annotated = AirplaneType.objects.filter(
            id=airplane_type.id
        ).annotate(
            airplane_park=Count("airplanes")
        ).first()

        url = detail_url(airplane_type.id)
        res = self.client.get(url)

        serializer = AirplaneTypeRetrieveSerializer(airplane_type_annotated)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "USA JET (America)"
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):
        payload = {
            "name": "American jet"
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        airplane_type = AirplaneType.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_delete_airplane_type(self):
        airplane_type = sample_airplane_type()

        url = detail_url(airplane_type.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
