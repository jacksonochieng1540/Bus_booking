from celery import shared_task
from bookings.models import Booking
from notifications.utils import send_booking_confirmation


@shared_task
def async_send_booking_confirmation(booking_id):
    """
    Celery async task to dispatch SMS booking confirmation.
    """
    try:
        booking = Booking.objects.select_related("trip__bus", "trip__route").get(pk=booking_id)
        send_booking_confirmation(booking)
        return True
    except Booking.DoesNotExist:
        return False
