from django.db import models


class Bus(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"Bus {self.plate_number} ({self.total_seats} seats)"


class Route(models.Model):
    departure_city = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.departure_city} to {self.destination_city} - {self.price}"


class Trip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="trips")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    departure_time = models.DateTimeField()

    def __str__(self):
        return f"Trip {self.pk}: {self.bus.plate_number} ({self.route}) at {self.departure_time}"

