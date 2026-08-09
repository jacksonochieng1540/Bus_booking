from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from fleets.models import Trip, Route
from bookings.models import Booking


@require_GET
def api_route_list(request):
    routes = Route.objects.all()
    data = [
        {
            "id": r.id,
            "departure_city": r.departure_city,
            "destination_city": r.destination_city,
            "price": str(r.price),
        }
        for r in routes
    ]
    return JsonResponse({"routes": data}, status=200)


@require_GET
def api_trip_list(request):
    departure = request.GET.get("departure", "").strip()
    destination = request.GET.get("destination", "").strip()

    trips = Trip.objects.select_related("bus", "route").filter(
        departure_time__gte=timezone.now()
    ).order_by("departure_time")

    if departure:
        trips = trips.filter(route__departure_city__icontains=departure)
    if destination:
        trips = trips.filter(route__destination_city__icontains=destination)

    data = []
    for trip in trips:
        confirmed_count = Booking.objects.filter(
            trip=trip, status=Booking.Status.CONFIRMED
        ).count()
        available_seats = max(0, trip.bus.total_seats - confirmed_count)
        data.append({
            "id": trip.id,
            "bus": {
                "id": trip.bus.id,
                "plate_number": trip.bus.plate_number,
                "total_seats": trip.bus.total_seats,
            },
            "route": {
                "id": trip.route.id,
                "departure_city": trip.route.departure_city,
                "destination_city": trip.route.destination_city,
                "price": str(trip.route.price),
            },
            "departure_time": trip.departure_time.isoformat(),
            "confirmed_seats_count": confirmed_count,
            "available_seats_count": available_seats,
        })

    return JsonResponse({"trips": data}, status=200)


@require_GET
def api_trip_detail(request, pk):
    try:
        trip = Trip.objects.select_related("bus", "route").get(pk=pk)
    except Trip.DoesNotExist:
        return JsonResponse({"error": "Trip not found."}, status=404)

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
            status = "confirmed"
        elif num in pending_seats:
            status = "pending"
        else:
            status = "available"
        seat_grid.append({"seat_number": num, "status": status})

    return JsonResponse({
        "id": trip.id,
        "bus": {
            "id": trip.bus.id,
            "plate_number": trip.bus.plate_number,
            "total_seats": trip.bus.total_seats,
        },
        "route": {
            "id": trip.route.id,
            "departure_city": trip.route.departure_city,
            "destination_city": trip.route.destination_city,
            "price": str(trip.route.price),
        },
        "departure_time": trip.departure_time.isoformat(),
        "available_seats_count": trip.bus.total_seats - len(confirmed_seats),
        "seat_grid": seat_grid,
    }, status=200)
