import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Airplane, AirplaneType, Crew
from air_service.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer
)

AIRPLANE_URL = reverse("air-service:airplane-list")


def detail_url(airplane_id):
    return reverse(
        "air-service:airplane-detail",
        args=(str(airplane_id),)
    )


def image_upload_url(airplane_id):
    """Return URL for recipe image upload"""
    return reverse(
        "air-service:airplane-upload-image",
        args=(str(airplane_id),)
    )


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.AIRPLANE_TYPE_SAMPLE = AirplaneType.objects.create(name="sample_name")

    def sample_airplane(self, **params) -> Airplane:
        defaults = {
            "name": "Test_city_name",
            "airplane_type": self.AIRPLANE_TYPE_SAMPLE,
            "rows": 30,
            "seats_in_row": 30
        }
        defaults.update(params)
        return Airplane.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        [self.sample_airplane() for _ in range(5)]

        res = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_airplanes_by_name(self):
        [self.sample_airplane(name=f"test{i + 1}") for i in range(5)]
        self.sample_airplane(name="filtered")
        self.sample_airplane(name="filtered2")

        res = self.client.get(
            AIRPLANE_URL,
            {"search_name": "filtered"}
        )
        incorrect_airplane = Airplane.objects.filter(
            name__exact="test0"
        )
        filtered_airplanes = Airplane.objects.filter(
            name__icontains="filtered"
        )
        serializer_correct_filter = AirplaneListSerializer(
            filtered_airplanes,
            many=True
        )
        serializer_incorrect_filter = AirplaneListSerializer(
            incorrect_airplane,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_airplanes_by_min_rows(self):
        [self.sample_airplane(rows=30) for _ in range(5)]
        self.sample_airplane(rows=35)
        self.sample_airplane(rows=25)

        res = self.client.get(
            AIRPLANE_URL,
            {"rows_min": 31}
        )
        incorrect_airplane = Airplane.objects.filter(rows__gte=26)
        filtered_airplanes = Airplane.objects.filter(rows__gte=31)
        serializer_correct_filter = AirplaneListSerializer(
            filtered_airplanes,
            many=True
        )
        serializer_incorrect_filter = AirplaneListSerializer(
            incorrect_airplane,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_airplanes_by_max_rows(self):
        [self.sample_airplane(rows=30) for _ in range(5)]
        self.sample_airplane(rows=35)
        self.sample_airplane(rows=25)

        res = self.client.get(
            AIRPLANE_URL,
            {"rows_max": 26}
        )
        incorrect_airplane = Airplane.objects.filter(rows__lte=31)
        filtered_airplanes = Airplane.objects.filter(rows__lte=26)
        serializer_correct_filter = AirplaneListSerializer(
            filtered_airplanes,
            many=True
        )
        serializer_incorrect_filter = AirplaneListSerializer(
            incorrect_airplane,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_airplanes_by_min_seats_in_row(self):
        [self.sample_airplane(seats_in_row=30) for _ in range(5)]
        self.sample_airplane(seats_in_row=35)
        self.sample_airplane(seats_in_row=25)

        res = self.client.get(
            AIRPLANE_URL,
            {"seats_in_row_min": 31}
        )
        incorrect_airplane = Airplane.objects.filter(seats_in_row__gte=26)
        filtered_airplanes = Airplane.objects.filter(seats_in_row__gte=31)
        serializer_correct_filter = AirplaneListSerializer(
            filtered_airplanes,
            many=True
        )
        serializer_incorrect_filter = AirplaneListSerializer(
            incorrect_airplane,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_airplanes_by_max_seats_in_row(self):
        [self.sample_airplane(seats_in_row=30) for _ in range(5)]
        self.sample_airplane(seats_in_row=35)
        self.sample_airplane(seats_in_row=25)

        res = self.client.get(
            AIRPLANE_URL,
            {"seats_in_row_max": 26}
        )
        incorrect_airplane = Airplane.objects.filter(seats_in_row__lte=31)
        filtered_airplanes = Airplane.objects.filter(seats_in_row__lte=26)
        serializer_correct_filter = AirplaneListSerializer(
            filtered_airplanes,
            many=True
        )
        serializer_incorrect_filter = AirplaneListSerializer(
            incorrect_airplane,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_airplanes_by_airplane_type_name(self):
        airplane_type = AirplaneType.objects.create(name="America jet")
        airplane_type_second = AirplaneType.objects.create(name="Simple jet")
        [self.sample_airplane() for _ in range(5)]
        self.sample_airplane(airplane_type=airplane_type)
        self.sample_airplane(airplane_type=airplane_type_second)

        res = self.client.get(
            AIRPLANE_URL,
            {"airplane_type_name": "America"}
        )
        incorrect_airplane = Airplane.objects.filter(
            airplane_type__name__icontains="Simple"
        )
        filtered_airplanes = Airplane.objects.filter(
            airplane_type__name__icontains="America"
        )
        serializer_correct_filter = AirplaneListSerializer(
            filtered_airplanes,
            many=True
        )
        serializer_incorrect_filter = AirplaneListSerializer(
            incorrect_airplane,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_airplanes_by_crew_last_name(self):
        airplane_1 = self.sample_airplane()
        airplane_2 = self.sample_airplane()
        crew_1 = Crew.objects.create(first_name="John", last_name="Doe")
        crew_2 = Crew.objects.create(first_name="Jane", last_name="Doe")
        crew_3 = Crew.objects.create(first_name="John", last_name="test")
        crew_4 = Crew.objects.create(first_name="Jane", last_name="test")
        airplane_1.crew.add(crew_1, crew_2)
        airplane_2.crew.add(crew_3, crew_4)

        res = self.client.get(
            AIRPLANE_URL,
            {"crew_person_last_name": "Doe"}
        )
        incorrect_airplane = Airplane.objects.filter(crew__last_name__iexact="John")
        filtered_airplanes = Airplane.objects.filter(crew__last_name__iexact="Doe")
        serializer_correct_filter = AirplaneListSerializer(
            filtered_airplanes,
            many=True
        )
        serializer_incorrect_filter = AirplaneListSerializer(
            incorrect_airplane,
            many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_order_airplanes_by_name(self):
        [self.sample_airplane(name=f"test{i + 1}") for i in range(8)]

        res = self.client.get(
            AIRPLANE_URL,
            {"ordering": "-name"}
        )
        res_another_ordering = self.client.get(
            AIRPLANE_URL,
            {"ordering": "name"}
        )

        ordered_airplanes = Airplane.objects.order_by("-name")
        serializer = AirplaneListSerializer(ordered_airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertNotEqual(
            res_another_ordering.data["results"],
            serializer.data
        )

    def test_retrieve_airplane_detail(self):
        airplane = self.sample_airplane()

        url = detail_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneRetrieveSerializer(airplane)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "America airplane",
            "airplane_type": self.AIRPLANE_TYPE_SAMPLE,
            "rows": 300,
            "seats_in_row": 400
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.AIRPLANE_TYPE_SAMPLE = AirplaneType.objects.create(name="sample_name")

    def sample_airplane(self, **params) -> Airplane:
        defaults = {
            "name": "Test_city_name",
            "airplane_type": self.AIRPLANE_TYPE_SAMPLE,
            "rows": 30,
            "seats_in_row": 30
        }
        defaults.update(params)
        return Airplane.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        payload = {
            "name": "America airplane",
            "airplane_type": self.AIRPLANE_TYPE_SAMPLE.id,
            "rows": 125,
            "seats_in_row": 100
        }

        res = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "airplane_type":
                self.assertEqual(payload[key], getattr(airplane, key).id)
                continue
            self.assertEqual(payload[key], getattr(airplane, key))

    def test_delete_airplane(self):
        airplane = self.sample_airplane()

        url = detail_url(airplane.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AirplaneImageUploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.AIRPLANE_TYPE_SAMPLE = AirplaneType.objects.create(name="sample_name")

    def sample_airplane(self, **params) -> Airplane:
        defaults = {
            "name": "Test_city_name",
            "airplane_type": self.AIRPLANE_TYPE_SAMPLE,
            "rows": 30,
            "seats_in_row": 30
        }
        defaults.update(params)
        return Airplane.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.airplane = self.sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        print(self.airplane.image.path)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(
            url,
            {"image": "not image"},
            format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list_should_not_work(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Test_city_name_2",
                    "airplane_type": self.AIRPLANE_TYPE_SAMPLE.id,
                    "rows": 30,
                    "seats_in_row": 30,
                    "image": ntf
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="Test_city_name_2")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data["results"][0].keys())
