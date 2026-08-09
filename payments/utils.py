import uuid
import logging
from payments.models import Payment
from bookings.models import Booking
from notifications.utils import send_booking_confirmation

logger = logging.getLogger(__name__)


def initiate_stk_push(booking, phone_number=None):
    """
    Initiates an M-Pesa STK Push payment request for a booking.
    """
    phone = phone_number or booking.passenger_phone
    amount = booking.trip.route.price

    merchant_id = f"MERCH-{uuid.uuid4().hex[:8].upper()}"
    checkout_id = f"CHECK-{uuid.uuid4().hex[:12].upper()}"

    payment = Payment.objects.create(
        booking=booking,
        amount=amount,
        phone_number=phone,
        merchant_request_id=merchant_id,
        checkout_request_id=checkout_id,
        status=Payment.Status.PENDING,
    )
    return payment


def process_payment_callback(payment_id, success=True, receipt_number=None):
    """
    Processes payment result callback from payment gateway (M-Pesa).
    Updates Payment and Booking statuses, and sends confirmation notification on success.
    """
    try:
        payment = Payment.objects.get(pk=payment_id)
    except Payment.DoesNotExist:
        return False, "Payment record not found."

    booking = payment.booking

    if success:
        receipt = receipt_number or f"MPESA-{uuid.uuid4().hex[:8].upper()}"
        payment.status = Payment.Status.COMPLETED
        payment.mpesa_receipt_number = receipt
        payment.save()

        booking.status = Booking.Status.CONFIRMED
        booking.save()

        send_booking_confirmation(booking)
        return True, "Payment completed successfully."
    else:
        payment.status = Payment.Status.FAILED
        payment.save()

        booking.status = Booking.Status.FAILED
        booking.save()
        return False, "Payment failed."
