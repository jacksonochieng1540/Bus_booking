from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from fleets.models import Trip, Route
from bookings.models import Booking


def trip_list(view_request):
    departure = view_request.GET.get("departure", "").strip()
    destination = view_request.GET.get("destination", "").strip()

    trips = Trip.objects.select_related("bus", "route").filter(
        departure_time__gte=timezone.now()
    ).order_by("departure_time")

    if departure:
        trips = trips.filter(route__departure_city__icontains=departure)
    if destination:
        trips = trips.filter(route__destination_city__icontains=destination)

    trip_data = []
    for trip in trips:
        confirmed_count = Booking.objects.filter(
            trip=trip, status=Booking.Status.CONFIRMED
        ).count()
        available_seats = max(0, trip.bus.total_seats - confirmed_count)
        trip_data.append({
            "trip": trip,
            "confirmed_count": confirmed_count,
            "available_seats": available_seats,
        })

    return render(
        view_request,
        "fleets/trip_list.html",
        {
            "trip_data": trip_data,
            "departure": departure,
            "destination": destination,
        },
    )


def trip_detail(view_request, pk):
    trip = get_object_or_404(Trip.objects.select_related("bus", "route"), pk=pk)

    confirmed_seats = set(
        Booking.objects.filter(
            trip=trip, status=Booking.Status.CONFIRMED
        ).values_list("seat_number", flat=True)
    )

    pending_seats = set(
        Booking.objects.filter(
            trip=trip, status=Booking.Status.PENDING
        ).values_list("seat_number", flat=True)
    )

    seat_grid = []
    for num in range(1, trip.bus.total_seats + 1):
        if num in confirmed_seats:
            seat_status = "confirmed"
        elif num in pending_seats:
            seat_status = "pending"
        else:
            seat_status = "available"
        seat_grid.append({"number": num, "status": seat_status})

    return render(
        view_request,
        "fleets/trip_detail.html",
        {
            "trip": trip,
            "seat_grid": seat_grid,
            "available_count": trip.bus.total_seats - len(confirmed_seats),
        },
    )
