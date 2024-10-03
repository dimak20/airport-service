from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Route, Airport, Country, City
from air_service.serializers import RouteListSerializer, RouteRetrieveSerializer

ROUTE_URL = reverse("air-service:route-list")


def detail_url(route_id):
    return reverse("air-service:route-detail", args=(str(route_id),))


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCityApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="America")
        cls.city = City.objects.create(name="Smaller America", country=cls.country)
        cls.AIRPORT_SAMPLE = Airport.objects.create(
            name="sample_name",
            closest_big_city=cls.city
        )

    def sample_route(self, **params) -> City:
        defaults = {
            "source": self.AIRPORT_SAMPLE,
            "destination": self.AIRPORT_SAMPLE,
            "distance": 1000
        }
        defaults.update(params)
        return Route.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_route_list(self):
        [self.sample_route() for i in range(5)]

        res = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_routes_by_distance_min(self):
        [self.sample_route(distance=950) for _ in range(5)]
        self.sample_route(distance=1000)
        self.sample_route(distance=1001)

        res = self.client.get(
            ROUTE_URL,
            {"distance_min": 1000}
        )
        incorrect_routes = Route.objects.filter(distance__gte=950)
        filtered_routes = Route.objects.filter(distance__gte=1000)
        serializer_correct_filter = RouteListSerializer(filtered_routes, many=True)
        serializer_incorrect_filter = RouteListSerializer(incorrect_routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_routes_by_distance_max(self):
        [self.sample_route(distance=950) for _ in range(5)]
        self.sample_route(distance=1000)
        self.sample_route(distance=1001)

        res = self.client.get(
            ROUTE_URL,
            {"distance_max": 960}
        )
        incorrect_routes = Route.objects.filter(distance__lte=1001)
        filtered_routes = Route.objects.filter(distance__lte=960)
        serializer_correct_filter = RouteListSerializer(filtered_routes, many=True)
        serializer_incorrect_filter = RouteListSerializer(incorrect_routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_routes_by_source_city(self):
        city_1 = City.objects.create(name="city_test_find", country=self.country)
        airport = Airport.objects.create(name="test_name", closest_big_city=city_1)
        [self.sample_route(distance=950) for _ in range(5)]
        self.sample_route(source=airport)
        self.sample_route(destination=airport)

        res = self.client.get(
            ROUTE_URL,
            {"source_city": "find"}
        )
        incorrect_routes = Route.objects.filter(
            source__closest_big_city__name__icontains="name"
        )
        filtered_routes = Route.objects.filter(
            source__closest_big_city__name__icontains="find"
        )
        serializer_correct_filter = RouteListSerializer(filtered_routes, many=True)
        serializer_incorrect_filter = RouteListSerializer(incorrect_routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_filter_routes_by_destination_city(self):
        city_1 = City.objects.create(name="city_test_find", country=self.country)
        airport = Airport.objects.create(name="test_name", closest_big_city=city_1)
        [self.sample_route(distance=950) for _ in range(5)]
        self.sample_route(source=airport)
        self.sample_route(destination=airport)

        res = self.client.get(
            ROUTE_URL,
            {"destination_city": "find"}
        )
        incorrect_routes = Route.objects.filter(
            destination__closest_big_city__name__icontains="name"
        )
        filtered_routes = Route.objects.filter(
            destination__closest_big_city__name__icontains="find"
        )
        serializer_correct_filter = RouteListSerializer(filtered_routes, many=True)
        serializer_incorrect_filter = RouteListSerializer(incorrect_routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_correct_filter.data, res.data["results"])
        self.assertNotIn(serializer_incorrect_filter.data, res.data["results"])

    def test_retrieve_route_detail(self):
        route = self.sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteRetrieveSerializer(route)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_route_forbidden(self):
        payload = {
            "source": self.AIRPORT_SAMPLE,
            "destination": self.AIRPORT_SAMPLE,
            "distance": 120
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="America")
        cls.city = City.objects.create(name="Smaller America", country=cls.country)
        cls.AIRPORT_SAMPLE = Airport.objects.create(
            name="sample_name",
            closest_big_city=cls.city
        )

    def sample_route(self, **params) -> City:
        defaults = {
            "source": self.AIRPORT_SAMPLE,
            "destination": self.AIRPORT_SAMPLE,
            "distance": 1000
        }
        defaults.update(params)
        return Route.objects.create(**defaults)

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        payload = {
            "source": self.AIRPORT_SAMPLE.id,
            "destination": self.AIRPORT_SAMPLE.id,
            "distance": 120
        }

        res = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "source" or key == "destination":
                self.assertEqual(payload[key], getattr(route, key).id)
                continue
            self.assertEqual(payload[key], getattr(route, key))

    def test_delete_route(self):
        route = self.sample_route()

        url = detail_url(route.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
