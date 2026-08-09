from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        FAILED = "FAILED", "Failed"

    trip = models.ForeignKey(
        "fleets.Trip",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=20)
    seat_number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "seat_number"],
                name="unique_trip_seat",
            )
        ]

    def __str__(self):
        return f"Booking {self.pk} - Seat {self.seat_number} ({self.status}) for {self.passenger_name}"
