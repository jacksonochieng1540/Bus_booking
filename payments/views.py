from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from bookings.models import Booking
from payments.models import Payment
from payments.utils import initiate_stk_push, process_payment_callback


def initiate_payment(view_request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    phone_number = view_request.POST.get("phone_number", booking.passenger_phone)

    payment = initiate_stk_push(booking, phone_number)
    messages.info(view_request, f"STK Push sent to {phone_number}. Complete payment on your phone.")

    return redirect("payments:payment_status", payment_id=payment.pk)


def simulate_callback(view_request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    action = view_request.GET.get("action", "success")

    if action == "success":
        success, msg = process_payment_callback(payment.pk, success=True)
        if success:
            messages.success(view_request, "M-Pesa payment received! Booking confirmed and SMS ticket sent.")
        else:
            messages.error(view_request, msg)
    else:
        process_payment_callback(payment.pk, success=False)
        messages.error(view_request, "Payment failed or was cancelled.")

    return redirect("bookings:booking_detail", pk=payment.booking.pk)


def payment_status(view_request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related("booking__trip__route"), pk=payment_id
    )
    return render(
        view_request,
        "payments/payment_status.html",
        {"payment": payment},
    )
