from django.contrib import admin
from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "passenger_name",
        "passenger_phone",
        "trip",
        "seat_number",
        "status",
    )
    list_filter = ("status", "trip__route")
    search_fields = ("passenger_name", "passenger_phone", "trip__bus__plate_number")
