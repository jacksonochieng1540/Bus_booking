from django.test import TestCase
from django.utils import timezone
from fleets.models import Bus, Route, Trip
from bookings.models import Booking
from notifications.models import NotificationLog
from notifications.utils import send_booking_confirmation


class NotificationTests(TestCase):
    def test_send_booking_confirmation(self):
        bus = Bus.objects.create(plate_number="KFF 300F", total_seats=30)
        route = Route.objects.create(
            departure_city="Nairobi",
            destination_city="Mombasa",
            price=2000.00,
        )
        trip = Trip.objects.create(
            bus=bus,
            route=route,
            departure_time=timezone.now(),
        )
        booking = Booking.objects.create(
            trip=trip,
            passenger_name="Grace Hopper",
            passenger_phone="+254766666666",
            seat_number=1,
            status=Booking.Status.CONFIRMED,
        )

        log = send_booking_confirmation(booking)
        self.assertIsNotNone(log)
        self.assertEqual(log.recipient, "+254766666666")
        self.assertEqual(log.status, NotificationLog.Status.SENT)
        self.assertIn("CONFIRMED", log.message)
