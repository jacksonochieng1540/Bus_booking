from django.test import TestCase
from django.utils import timezone
from fleets.models import Bus, Route, Trip
from bookings.models import Booking
from payments.models import Payment
from payments.utils import initiate_stk_push, process_payment_callback
from notifications.models import NotificationLog


class PaymentTests(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(plate_number="KEE 200E", total_seats=40)
        self.route = Route.objects.create(
            departure_city="Nairobi",
            destination_city="Kisumu",
            price=1500.00,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            route=self.route,
            departure_time=timezone.now(),
        )
        self.booking = Booking.objects.create(
            trip=self.trip,
            passenger_name="Sam Wilson",
            passenger_phone="+254755555555",
            seat_number=8,
            status=Booking.Status.PENDING,
        )

    def test_initiate_stk_push(self):
        payment = initiate_stk_push(self.booking)
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, 1500.00)
        self.assertEqual(payment.status, Payment.Status.PENDING)

    def test_process_payment_callback_success(self):
        payment = initiate_stk_push(self.booking)
        success, msg = process_payment_callback(
            payment.pk,
            success=True,
            receipt_number="MP12345",
        )
        self.assertTrue(success)
        payment.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.COMPLETED)
        self.assertEqual(payment.mpesa_receipt_number, "MP12345")
        self.assertEqual(self.booking.status, Booking.Status.CONFIRMED)
        self.assertEqual(
            NotificationLog.objects.filter(booking=self.booking).count(), 1
        )
