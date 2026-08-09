from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from fleets.models import Bus, Route, Trip


class FleetsModelTests(TestCase):
    def test_create_bus(self):
        bus = Bus.objects.create(plate_number="KAA 123A", total_seats=45)
        self.assertEqual(bus.plate_number, "KAA 123A")
        self.assertEqual(bus.total_seats, 45)

    def test_create_route(self):
        route = Route.objects.create(
            departure_city="Nairobi",
            destination_city="Mombasa",
            price=1500.00,
        )
        self.assertEqual(route.departure_city, "Nairobi")
        self.assertEqual(route.destination_city, "Mombasa")

    def test_create_trip(self):
        bus = Bus.objects.create(plate_number="KBB 456B", total_seats=30)
        route = Route.objects.create(
            departure_city="Nairobi",
            destination_city="Kisumu",
            price=1200.00,
        )
        now = timezone.now()
        trip = Trip.objects.create(bus=bus, route=route, departure_time=now)
        self.assertEqual(trip.bus, bus)
        self.assertEqual(trip.route, route)


class FleetsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.bus = Bus.objects.create(plate_number="KAA 123A", total_seats=45)
        self.route = Route.objects.create(
            departure_city="Nairobi",
            destination_city="Mombasa",
            price=1500.00,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            route=self.route,
            departure_time=timezone.now(),
        )

    def test_api_route_list(self):
        response = self.client.get(reverse("fleets:api_route_list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("routes", data)
        self.assertEqual(len(data["routes"]), 1)

    def test_api_trip_list(self):
        response = self.client.get(reverse("fleets:api_trip_list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("trips", data)

    def test_api_trip_detail(self):
        response = self.client.get(reverse("fleets:api_trip_detail", args=[self.trip.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.trip.pk)
        self.assertEqual(len(data["seat_grid"]), 45)
