import django_filters
from django.db.models.functions import TruncHour


class RouteFilter(django_filters.FilterSet):
    distance_min = django_filters.NumberFilter(field_name="distance", lookup_expr="gte")
    distance_max = django_filters.NumberFilter(field_name="distance", lookup_expr="lte")
    source_city = django_filters.CharFilter(
        field_name="source__closest_big_city__name", lookup_expr="icontains"
    )
    destination_city = django_filters.CharFilter(
        field_name="destination__closest_big_city__name", lookup_expr="icontains"
    )


class FlightFilter(django_filters.FilterSet):
    route_ids = django_filters.CharFilter(method="filter_by_route_ids")
    airplane_name = django_filters.CharFilter(
        field_name="airplane__name", lookup_expr="icontains"
    )
    departure_time_hour = django_filters.DateTimeFilter(method="filter_by_hour")
    departure_time_hour_after = django_filters.DateTimeFilter(
        method="filter_by_hour_gte"
    )
    departure_time_hour_before = django_filters.DateTimeFilter(
        method="filter_by_hour_lte"
    )

    def filter_by_hour(self, queryset, name, value):
        return queryset.annotate(departure_hour=TruncHour("departure_time")).filter(
            departure_hour=value
        )

    def filter_by_hour_gte(self, queryset, name, value):
        return queryset.annotate(departure_hour=TruncHour("departure_time")).filter(
            departure_hour__gte=value
        )

    def filter_by_hour_lte(self, queryset, name, value):
        return queryset.annotate(departure_hour=TruncHour("departure_time")).filter(
            departure_hour__lte=value
        )

    def filter_by_route_ids(self, queryset, name, value):
        if value:
            route_ids = [int(i) for i in value.split(",")]
            return queryset.filter(route__id__in=route_ids)
        return queryset


class CountryFilter(django_filters.FilterSet):
    country_name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")


class CityFilter(django_filters.FilterSet):
    city_name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    country_name = django_filters.CharFilter(
        field_name="country__name", lookup_expr="icontains"
    )


class CrewFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        field_name="first_name", lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(
        field_name="last_name", lookup_expr="icontains"
    )


class AirplaneTypeFilter(django_filters.FilterSet):
    search_name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")


class AirportFilter(django_filters.FilterSet):
    search_name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    closest_city_name = django_filters.CharFilter(
        field_name="closest_big_city__name", lookup_expr="icontains"
    )


class AirplaneFilter(django_filters.FilterSet):
    search_name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    rows_min = django_filters.NumberFilter(field_name="rows", lookup_expr="gte")
    rows_max = django_filters.NumberFilter(field_name="rows", lookup_expr="lte")
    seats_in_row_min = django_filters.NumberFilter(
        field_name="seats_in_row", lookup_expr="gte"
    )
    seats_in_row_max = django_filters.NumberFilter(
        field_name="seats_in_row", lookup_expr="lte"
    )
    airplane_type_name = django_filters.CharFilter(
        field_name="airplane_type__name", lookup_expr="icontains"
    )
    crew_person_last_name = django_filters.CharFilter(
        field_name="crew__last_name", lookup_expr="iexact"
    )
