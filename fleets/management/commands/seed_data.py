from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from fleets.models import Bus, Route, Trip


class Command(BaseCommand):
    help = "Seeds the database with initial buses, routes, and scheduled express trips."

    def handle(self, *args, **options):
        # Create default buses
        bus1, _ = Bus.objects.get_or_create(plate_number="KCD 101A", defaults={"total_seats": 45})
        bus2, _ = Bus.objects.get_or_create(plate_number="KDB 502B", defaults={"total_seats": 52})
        bus3, _ = Bus.objects.get_or_create(plate_number="KCY 909C", defaults={"total_seats": 36})
        bus4, _ = Bus.objects.get_or_create(plate_number="KDD 333D", defaults={"total_seats": 48})

        # Create default routes
        r1, _ = Route.objects.get_or_create(
            departure_city="Nairobi", destination_city="Mombasa", defaults={"price": 1500.00}
        )
        r2, _ = Route.objects.get_or_create(
            departure_city="Nairobi", destination_city="Kisumu", defaults={"price": 1200.00}
        )
        r3, _ = Route.objects.get_or_create(
            departure_city="Mombasa", destination_city="Nairobi", defaults={"price": 1500.00}
        )
        r4, _ = Route.objects.get_or_create(
            departure_city="Nairobi", destination_city="Eldoret", defaults={"price": 1100.00}
        )
        r5, _ = Route.objects.get_or_create(
            departure_city="Kisumu", destination_city="Nairobi", defaults={"price": 1200.00}
        )

        now = timezone.now()

        # Create scheduled trips for today and upcoming days
        Trip.objects.get_or_create(bus=bus1, route=r1, departure_time=now + timedelta(hours=3))
        Trip.objects.get_or_create(bus=bus2, route=r2, departure_time=now + timedelta(hours=5))
        Trip.objects.get_or_create(bus=bus3, route=r3, departure_time=now + timedelta(hours=8))
        Trip.objects.get_or_create(bus=bus4, route=r4, departure_time=now + timedelta(days=1, hours=2))
        Trip.objects.get_or_create(bus=bus1, route=r5, departure_time=now + timedelta(days=1, hours=6))

        self.stdout.write(self.style.SUCCESS("Successfully seeded buses, routes, and express trips!"))
