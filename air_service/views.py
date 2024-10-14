from django.db.models import Count, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from air_service.filters import (
    RouteFilter,
    FlightFilter,
    CountryFilter,
    CityFilter,
    CrewFilter,
    AirplaneTypeFilter,
    AirportFilter,
    AirplaneFilter,
)
from air_service.models import (
    Country,
    City,
    Crew,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Ticket,
    Order,
)
from air_service.ordering import AirServiceOrdering
from air_service.serializers import (
    CountrySerializer,
    CitySerializer,
    CrewSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    AirplaneSerializer,
    RouteSerializer,
    FlightSerializer,
    TicketSerializer,
    OrderSerializer,
    CountryRetrieveSerializer,
    CityListSerializer,
    CityRetrieveSerializer,
    CrewListSerializer,
    CrewRetrieveSerializer,
    AirplaneTypeRetrieveSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    TicketListSerializer,
    OrderListSerializer,
    TicketRetrieveSerializer,
    OrderRetrieveSerializer,
    AirplaneImageSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    model = Country
    queryset = Country.objects.all()
    ordering_fields = ("pk", "name")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CountryFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CountryRetrieveSerializer

        return CountrySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related()

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CityViewSet(viewsets.ModelViewSet):
    model = City
    queryset = City.objects.select_related()
    ordering_fields = ("pk", "name")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CityFilter

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer

        if self.action == "retrieve":
            return CityRetrieveSerializer

        return CitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related()

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    model = Crew
    queryset = Crew.objects.all()
    ordering_fields = ("pk", "first_name", "last_name")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CrewFilter

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        if self.action == "retrieve":
            return CrewRetrieveSerializer

        return CrewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related("airplanes")

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    model = AirplaneType
    queryset = AirplaneType.objects.all()
    ordering_fields = ("pk", "name")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirplaneTypeFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneTypeRetrieveSerializer

        return AirplaneTypeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related().annotate(
                airplane_park=Count("airplanes")
            )

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    model = Airport
    queryset = Airport.objects.select_related()
    ordering_fields = ("pk", "name")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirportFilter

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        if self.action == "retrieve":
            return AirportRetrieveSerializer

        return AirportSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related()

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    model = Airplane
    queryset = Airplane.objects.select_related()
    ordering_fields = ("pk", "name")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirplaneFilter

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneRetrieveSerializer

        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related().prefetch_related("crew")

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[
            IsAdminUser,
        ],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    model = Route
    queryset = Route.objects.select_related()
    ordering_fields = ("pk", "distance")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RouteFilter

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteRetrieveSerializer

        return RouteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related()

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    model = Flight
    queryset = Flight.objects.select_related()
    ordering_fields = ("pk", "departure_time", "arrival_time")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FlightFilter

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightRetrieveSerializer

        return FlightSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related().annotate(
                tickets_available=
                F("airplane__rows")
                * F("airplane__seats_in_row")
                - Count("tickets")
            )

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TicketViewSet(viewsets.ModelViewSet):
    model = Ticket
    serializer_class = TicketSerializer
    ordering_fields = ("pk",)
    queryset = Ticket.objects.select_related()
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = self.queryset.filter(order__user=self.request.user)
        if self.action == "list":
            queryset = queryset.select_related()

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        if self.action == "retrieve":
            return TicketRetrieveSerializer

        return TicketSerializer

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    model = Order
    serializer_class = OrderSerializer
    ordering_fields = ("pk",)
    queryset = Order.objects.select_related()
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__flight__route__source", "tickets__flight__route__destination"
            )

        ordering_fields = AirServiceOrdering.get_ordering_fields(
            self.request, list(self.ordering_fields)
        )

        return queryset.order_by(*ordering_fields)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderRetrieveSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @method_decorator(cache_page(60 * 15))
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                description="Comma-separated list of fields to order by. Prefix with `-` to sort in descending order.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
