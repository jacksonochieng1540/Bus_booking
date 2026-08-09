import logging
from notifications.models import NotificationLog

logger = logging.getLogger(__name__)


def send_booking_confirmation(booking):
    """
    Dispatches SMS/Email notification to the passenger upon successful booking confirmation.
    """
    message = (
        f"Dear {booking.passenger_name}, your booking (ID #{booking.pk}) for "
        f"{booking.trip.route.departure_city} -> {booking.trip.route.destination_city} "
        f"on seat {booking.seat_number} has been CONFIRMED. "
        f"Departure: {booking.trip.departure_time.strftime('%Y-%m-%d %H:%M')}. "
        f"Thank you for choosing Bus Sacco!"
    )
    try:
        log = NotificationLog.objects.create(
            booking=booking,
            recipient=booking.passenger_phone,
            message=message,
            status=NotificationLog.Status.SENT,
        )
        logger.info(f"Notification sent to {booking.passenger_phone}: {log.pk}")
        return log
    except Exception as e:
        logger.error(f"Failed to send notification for booking {booking.pk}: {e}")
        return None
