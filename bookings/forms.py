from django import forms
from django.utils.html import strip_tags
from bookings.models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["passenger_name", "passenger_phone", "seat_number"]

    def __init__(self, *args, trip=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.trip = trip or (
            self.instance.trip
            if self.instance and hasattr(self.instance, "trip") and self.instance.trip_id
            else None
        )

    def clean_passenger_name(self):
        name = self.cleaned_data.get("passenger_name", "").strip()
        sanitized = strip_tags(name)
        if not sanitized:
            raise forms.ValidationError("Please enter a valid passenger name.")
        return sanitized

    def clean_passenger_phone(self):
        phone = self.cleaned_data.get("passenger_phone", "").strip()
        sanitized = strip_tags(phone)
        if not sanitized:
            raise forms.ValidationError("Please enter a valid phone number.")
        return sanitized

    def clean_seat_number(self):
        seat_number = self.cleaned_data.get("seat_number")
        if seat_number is None:
            return seat_number

        trip = self.trip
        if not trip:
            raise forms.ValidationError("Trip context is required to validate the seat number.")

        if trip.bus and seat_number > trip.bus.total_seats:
            raise forms.ValidationError(
                f"Seat number {seat_number} exceeds the bus total capacity of {trip.bus.total_seats}."
            )

        if seat_number < 1:
            raise forms.ValidationError("Seat number must be a positive integer.")

        existing_booking = Booking.objects.filter(
            trip=trip,
            seat_number=seat_number,
            status=Booking.Status.CONFIRMED,
        )
        if self.instance and self.instance.pk:
            existing_booking = existing_booking.exclude(pk=self.instance.pk)

        if existing_booking.exists():
            raise forms.ValidationError(
                f"Seat number {seat_number} is already booked and confirmed."
            )

        return seat_number

    def save(self, commit=True):
        booking = super().save(commit=False)
        if self.trip:
            booking.trip = self.trip
        if commit:
            booking.save()
        return booking
