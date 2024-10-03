from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Airport, Country, City, Route, AirplaneType, Airplane, Flight, Order, Ticket
from air_service.serializers import OrderListSerializer, OrderRetrieveSerializer

ORDER_URL = reverse("air-service:order-list")


def detail_url(order_id):
    return reverse("air-service:order-detail", args=(str(order_id),))


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
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
        cls.flight = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(days=1)
        )

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def sample_order(self, user: get_user_model() = None) -> Order:
        if not user:
            user = self.user
        return Order.objects.create(user=user)

    def sample_ticket(self, **params) -> Ticket:
        order = Order.objects.create(
            user=self.user
        )
        defaults = {
            "row": 1,
            "seat": 1,
            "flight": self.flight,
            "order": order

        }
        defaults.update(params)
        return Ticket.objects.create(**defaults)

    def test_order_list(self):
        [self.sample_order() for _ in range(5)]
        ticket = self.sample_ticket()
        order = self.sample_order()
        order.tickets.add(ticket)

        res = self.client.get(ORDER_URL)
        orders = Order.objects.all().order_by("pk")
        serializer = OrderListSerializer(orders, many=True)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_list_only_request_user(self):
        user = get_user_model().objects.create(
            email="email@email.com",
            password="test_123_pass"
        )

        [self.sample_order() for _ in range(5)]

        [self.sample_order(user=user) for _ in range(5)]

        res = self.client.get(ORDER_URL)
        orders = Order.objects.order_by("-created_at")
        orders_user = Order.objects.filter(user=self.user).order_by("pk")
        serializer_all_orders = OrderListSerializer(orders, many=True)
        serializer_request_user = OrderListSerializer(orders_user, many=True)
        self.assertNotEqual(res.data["results"], serializer_all_orders.data)
        self.assertEqual(res.data["results"], serializer_request_user.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_tickets_by_pk(self):
        [self.sample_order() for _ in range(5)]

        res = self.client.get(
            ORDER_URL,
            {"ordering": "-pk"}
        )
        res_another_ordering = self.client.get(
            ORDER_URL,
            {"ordering": "pk"}
        )

        ordered_orders = Order.objects.order_by("-pk")
        serializer = OrderListSerializer(ordered_orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertNotEqual(
            res_another_ordering.data["results"],
            serializer.data
        )

    def test_retrieve_order_detail(self):
        order = self.sample_order()
        url = detail_url(order.id)
        res = self.client.get(url)

        serializer = OrderRetrieveSerializer(order)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_order(self):
        order = self.sample_order()

        url = detail_url(order.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
