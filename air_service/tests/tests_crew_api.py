from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Crew
from air_service.serializers import CrewListSerializer, CrewRetrieveSerializer

CREW_URL = reverse("air-service:crew-list")


def detail_url(crew_id):
    return reverse("air-service:crew-detail", args=(str(crew_id),))


def sample_crew(**params) -> Crew:
    defaults = {
        "first_name": "Test_first_name",
        "last_name": "Test_last_name",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_country_list(self):
        [sample_crew(
            first_name=f"test{i}",
            last_name=f"test{i + 1}"
        ) for i in range(5)
        ]

        res = self.client.get(CREW_URL)
        crews = Crew.objects.all()
        serializer = CrewListSerializer(crews, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_crew_by_first_name(self):
        [sample_crew(
            first_name=f"test{i}",
            last_name=f"test{i + 1}"
        ) for i in range(5)
        ]
        sample_crew(first_name="filtered", last_name="last")
        sample_crew(first_name="filtered2", last_name="last")

        res = self.client.get(
            CREW_URL,
            {"first_name": "filtered"}
        )
        incorrect_crew = Crew.objects.filter(first_name__exact="test0")
        filtered_crews = Crew.objects.filter(first_name__icontains="filtered")
        serializer_correct_filter = CrewListSerializer(filtered_crews, many=True)
        serializer_incorrect_filter = CrewListSerializer(incorrect_crew, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_crew_by_first_and_last_name(self):
        [sample_crew(
            first_name=f"test{i}",
            last_name=f"test{i + 1}"
        ) for i in range(5)
        ]
        sample_crew(first_name="filtered", last_name="last")
        sample_crew(first_name="filtered2", last_name="last")
        sample_crew(first_name="filtered3", last_name="no_surname")

        res = self.client.get(
            CREW_URL,
            {
                "first_name": "filtered",
                "last_name": "last"
            }
        )
        incorrect_crew = Crew.objects.filter(first_name__icontains="filtered")
        filtered_crews = Crew.objects.filter(first_name__icontains="filtered", last_name__icontains="last")
        serializer_correct_filter = CrewListSerializer(filtered_crews, many=True)
        serializer_incorrect_filter = CrewListSerializer(incorrect_crew, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_order_crew_by_name(self):
        [sample_crew(
            first_name=f"test{i}",
            last_name=f"test{i + 1}"
        ) for i in range(10)
        ]

        res = self.client.get(
            CREW_URL,
            {"ordering": "-first_name"}
        )
        res_another_ordering = self.client.get(
            CREW_URL,
            {"ordering": "first_name"}
        )

        ordered_crews = Crew.objects.order_by("-first_name")
        serializer = CrewListSerializer(ordered_crews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertNotEqual(
            res_another_ordering.data["results"],
            serializer.data
        )

    def test_retrieve_crew_detail(self):
        crew = sample_crew()

        url = detail_url(crew.id)
        res = self.client.get(url)

        serializer = CrewRetrieveSerializer(crew)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "American",
            "last_name": "American",
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "American",
            "last_name": "American",
        }

        res = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_delete_crew(self):
        crew = sample_crew()

        url = detail_url(crew.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
