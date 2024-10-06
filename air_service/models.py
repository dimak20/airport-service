import pathlib
import uuid
from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import CASCADE, UniqueConstraint
from django.utils.text import slugify


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.name = " ".join([word.lower().capitalize() for word in self.name.split()])
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=CASCADE, related_name="cities")

    class Meta:
        ordering = ["name", "country__name"]
        verbose_name_plural = "cities"
        unique_together = ["name", "country"]

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.name = self.name.lower().capitalize()
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"{self.name} ({self.country.name})"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.name = self.name.lower().capitalize()
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return self.name.capitalize()

    class Meta:
        ordering = ["name"]


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(City, on_delete=CASCADE, related_name="airports")

    def __str__(self) -> str:
        return f"{self.name} (closest city - {self.closest_big_city})"


def airplane_image_path(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("upload/airplanes/") / pathlib.Path(filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=CASCADE, related_name="airplanes")
    crew = models.ManyToManyField(Crew, related_name="airplanes", blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=airplane_image_path)

    def __str__(self) -> str:
        return (
            f"{self.name} (type - {self.airplane_type}). "
            f"Rows: {self.rows}. Seats_in_row: {self.seats_in_row}"
        )

    @property
    def capacity(self):
        return int(self.rows * self.seats_in_row)


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=CASCADE, related_name="source_routes")
    destination = models.ForeignKey(Airport, on_delete=CASCADE, related_name="destination_routes")
    distance = models.PositiveIntegerField()

    class Meta:
        ordering = ["source"]

    def __str__(self) -> str:
        return (
            f"From {self.source.closest_big_city.name} "
            f"to {self.destination.closest_big_city.name}"
        )

    @property
    def distance_in_km(self) -> int:
        return self.distance

    @property
    def distance_in_nm(self) -> int:
        return round(self.distance / 1.852)


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    @property
    def flight_time(self) -> str:
        delta = self.arrival_time - self.departure_time
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes = remainder // 60
        return f"{int(hours)} h {int(minutes)} min"

    @staticmethod
    def validate_time(departure_time: datetime, arrival_time: datetime, error_to_raise):
        if arrival_time < departure_time:
            raise error_to_raise(
                {
                    "arrival_time": "Must be higher than departure_time"
                }
            )

    def clean(self):
        self.validate_time(self.departure_time, self.arrival_time, ValueError)

    def __str__(self) -> str:
        return (
            f"Route: {self.route}. Boarding {self.airplane}."
            f"Departure - Arrival: {self.departure_time} - {self.arrival_time}"
        )


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight, on_delete=CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=CASCADE, related_name="tickets")
    notification_sent = models.BooleanField(default=False, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["seat", "row", "flight"],
                name="unique_ticket_seat_row_flight"
            )
        ]
        ordering = ["seat", "row"]

    def __str__(self) -> str:
        return f"Flight: {self.flight.route} (row: {self.row}, seat: {self.seat}"

    def clean(self):
        Ticket.validate_seat_row(
            self.seat,
            self.row,
            self.flight.airplane.seats_in_row,
            self.flight.airplane.rows,
            ValueError
        )

    @staticmethod
    def validate_seat_row(
            seat,
            row,
            airplane_seats,
            airplane_rows,
            error_to_raise
    ):
        if not (1 <= seat <= airplane_seats):
            raise error_to_raise(
                {
                    "seat": "seat must be in range of airplane seats"
                }
            )

        if not (1 <= row <= airplane_rows):
            raise error_to_raise(
                {
                    "row": "row must be in range of airplane rows"
                }
            )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(force_insert, force_update, using, update_fields)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.created_at)
