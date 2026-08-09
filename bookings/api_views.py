import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from django.db import IntegrityError
from fleets.models import Trip
from bookings.models import Booking
from bookings.forms import BookingForm


@csrf_exempt
@require_http_methods(["POST"])
def api_create_booking(request, trip_id):
    try:
        trip = Trip.objects.select_related("bus", "route").get(pk=trip_id)
    except Trip.DoesNotExist:
        return JsonResponse({"error": "Trip not found."}, status=404)

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
    except Exception:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    form = BookingForm(data, trip=trip)
    if form.is_valid():
        try:
            booking = form.save()
            return JsonResponse({
                "message": "Booking created successfully.",
                "booking": {
                    "id": booking.id,
                    "passenger_name": booking.passenger_name,
                    "passenger_phone": booking.passenger_phone,
                    "seat_number": booking.seat_number,
                    "status": booking.status,
                    "trip_id": booking.trip.id,
                    "price": str(booking.trip.route.price),
                }
            }, status=201)
        except IntegrityError:
            return JsonResponse({
                "error": "This seat has already been reserved for this trip."
            }, status=409)
    else:
        return JsonResponse({"errors": form.errors}, status=400)


@require_GET
def api_booking_detail(request, pk):
    try:
        booking = Booking.objects.select_related("trip__bus", "trip__route").get(pk=pk)
    except Booking.DoesNotExist:
        return JsonResponse({"error": "Booking not found."}, status=404)

    return JsonResponse({
        "booking": {
            "id": booking.id,
            "passenger_name": booking.passenger_name,
            "passenger_phone": booking.passenger_phone,
            "seat_number": booking.seat_number,
            "status": booking.status,
            "trip": {
                "id": booking.trip.id,
                "bus_plate": booking.trip.bus.plate_number,
                "departure_city": booking.trip.route.departure_city,
                "destination_city": booking.trip.route.destination_city,
                "departure_time": booking.trip.departure_time.isoformat(),
                "price": str(booking.trip.route.price),
            }
        }
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def api_booking_cancel(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return JsonResponse({"error": "Booking not found."}, status=404)

    if booking.status == Booking.Status.PENDING:
        booking.delete()
        return JsonResponse({"message": "Pending booking cancelled successfully."}, status=200)
    else:
        return JsonResponse({"error": "Only pending bookings can be cancelled."}, status=400)
