from django.contrib import admin
from fleets.models import Bus, Route, Trip


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "total_seats")
    search_fields = ("plate_number",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("departure_city", "destination_city", "price")
    search_fields = ("departure_city", "destination_city")
    list_filter = ("departure_city", "destination_city")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "bus", "route", "departure_time")
    list_filter = ("departure_time", "route__departure_city")
    search_fields = ("bus__plate_number", "route__departure_city", "route__destination_city")
