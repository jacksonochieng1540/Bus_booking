from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from fleets.models import Trip
from bookings.models import Booking
from bookings.forms import BookingForm
from payments.models import Payment


def create_booking(view_request, trip_id):
    trip = get_object_or_404(Trip.objects.select_related("bus", "route"), pk=trip_id)
    initial_seat = view_request.GET.get("seat")

    initial_data = {}
    if initial_seat and initial_seat.isdigit():
        initial_data["seat_number"] = int(initial_seat)

    if view_request.method == "POST":
        form = BookingForm(view_request.POST, trip=trip)
        if form.is_valid():
            try:
                booking = form.save()
                messages.success(view_request, f"Booking reserved for Seat #{booking.seat_number}!")
                return redirect("bookings:booking_detail", pk=booking.pk)
            except IntegrityError:
                form.add_error(
                    "seat_number",
                    "This seat has just been reserved by another passenger. Please select a different seat."
                )
    else:
        form = BookingForm(initial=initial_data, trip=trip)

    return render(
        view_request,
        "bookings/booking_form.html",
        {
            "form": form,
            "trip": trip,
        },
    )


def booking_detail(view_request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related("trip__bus", "trip__route"), pk=pk
    )
    latest_payment = Payment.objects.filter(booking=booking).order_by("-created_at").first()

    return render(
        view_request,
        "bookings/booking_detail.html",
        {
            "booking": booking,
            "payment": latest_payment,
        },
    )


def booking_cancel(view_request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status == Booking.Status.PENDING:
        booking.delete()
        messages.info(view_request, "Your pending booking has been canceled.")
    return redirect("fleets:trip_list")
