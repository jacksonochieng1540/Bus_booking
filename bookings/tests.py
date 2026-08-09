from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from fleets.models import Bus, Route, Trip
from bookings.models import Booking


class BookingModelTests(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(plate_number="KCC 789C", total_seats=50)
        self.route = Route.objects.create(
            departure_city="Nairobi",
            destination_city="Nakuru",
            price=800.00,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            route=self.route,
            departure_time=timezone.now(),
        )

    def test_create_booking_success(self):
        booking = Booking.objects.create(
            trip=self.trip,
            passenger_name="John Doe",
            passenger_phone="+254712345678",
            seat_number=12,
            status=Booking.Status.CONFIRMED,
        )
        self.assertEqual(booking.seat_number, 12)
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_double_booking_prevention_unique_constraint(self):
        Booking.objects.create(
            trip=self.trip,
            passenger_name="Jane Doe",
            passenger_phone="+254787654321",
            seat_number=5,
            status=Booking.Status.PENDING,
        )
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                trip=self.trip,
                passenger_name="Bob Smith",
                passenger_phone="+254700000000",
                seat_number=5,
                status=Booking.Status.CONFIRMED,
            )


from bookings.forms import BookingForm


class BookingFormTests(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(plate_number="KDD 100D", total_seats=30)
        self.route = Route.objects.create(
            departure_city="Nairobi",
            destination_city="Eldoret",
            price=1000.00,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            route=self.route,
            departure_time=timezone.now(),
        )

    def test_valid_booking_form(self):
        form_data = {
            "passenger_name": "Alice Smith",
            "passenger_phone": "+254711111111",
            "seat_number": 10,
        }
        form = BookingForm(data=form_data, trip=self.trip)
        self.assertTrue(form.is_valid())
        booking = form.save()
        self.assertEqual(booking.seat_number, 10)
        self.assertEqual(booking.trip, self.trip)

    def test_seat_number_exceeds_bus_capacity(self):
        form_data = {
            "passenger_name": "Bob Brown",
            "passenger_phone": "+254722222222",
            "seat_number": 35,  # Bus capacity is 30
        }
        form = BookingForm(data=form_data, trip=self.trip)
        self.assertFalse(form.is_valid())
        self.assertIn("seat_number", form.errors)

    def test_seat_number_already_taken_by_confirmed_booking(self):
        Booking.objects.create(
            trip=self.trip,
            passenger_name="Charlie Green",
            passenger_phone="+254733333333",
            seat_number=15,
            status=Booking.Status.CONFIRMED,
        )
        form_data = {
            "passenger_name": "David White",
            "passenger_phone": "+254744444444",
            "seat_number": 15,
        }
        form = BookingForm(data=form_data, trip=self.trip)
        self.assertFalse(form.is_valid())
        self.assertIn("seat_number", form.errors)


