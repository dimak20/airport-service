from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import Airport, Country, City, Route, AirplaneType, Airplane, Flight, Order, Ticket
from air_service.serializers import TicketListSerializer, \
    TicketRetrieveSerializer

TICKET_URL = reverse("air-service:ticket-list")


def detail_url(ticket_id):
    return reverse("air-service:ticket-detail", args=(str(ticket_id),))


class UnauthenticatedTicketApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketApiTests(TestCase):
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

    def test_tickets_list(self):
        [self.sample_ticket(row=i + 1, seat=i + 1) for i in range(5)]

        res = self.client.get(TICKET_URL)
        tickets = Ticket.objects.all()
        serializer = TicketListSerializer(tickets, many=True)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_order_tickets_by_pk(self):
        [self.sample_ticket(row=i + 1, seat=i + 1) for i in range(5)]

        res = self.client.get(
            TICKET_URL,
            {"ordering": "-pk"}
        )
        res_another_ordering = self.client.get(
            TICKET_URL,
            {"ordering": "pk"}
        )

        ordered_tickets = Ticket.objects.order_by("-pk")
        serializer = TicketListSerializer(ordered_tickets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertNotEqual(
            res_another_ordering.data["results"],
            serializer.data
        )

    def test_retrieve_ticket_detail(self):
        ticket = self.sample_ticket()
        url = detail_url(ticket.id)
        res = self.client.get(url)

        serializer = TicketRetrieveSerializer(ticket)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_ticket_allowed(self):
        ticket = self.sample_ticket()
        payload = {
            "row": 11,
            "seat": 12,
            "flight": self.flight.id
        }
        url = detail_url(ticket.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_ticket(self):
        ticket = self.sample_ticket()

        url = detail_url(ticket.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
