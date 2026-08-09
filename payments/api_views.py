import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from bookings.models import Booking
from payments.models import Payment
from payments.utils import initiate_stk_push, process_payment_callback


@csrf_exempt
@require_http_methods(["POST"])
def api_initiate_payment(request):
    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
    except Exception:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    booking_id = data.get("booking_id")
    phone_number = data.get("phone_number")

    if not booking_id:
        return JsonResponse({"error": "booking_id is required."}, status=400)

    try:
        booking = Booking.objects.select_related("trip__route").get(pk=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({"error": "Booking not found."}, status=404)

    payment = initiate_stk_push(booking, phone_number)
    return JsonResponse({
        "message": "STK Push initiated successfully.",
        "payment": {
            "id": payment.id,
            "merchant_request_id": payment.merchant_request_id,
            "checkout_request_id": payment.checkout_request_id,
            "amount": str(payment.amount),
            "phone_number": payment.phone_number,
            "status": payment.status,
        }
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def api_payment_callback(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment record not found."}, status=404)

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
    except Exception:
        data = {}

    success = data.get("success", True)
    receipt_number = data.get("mpesa_receipt_number")

    ok, msg = process_payment_callback(payment.pk, success=success, receipt_number=receipt_number)
    if ok:
        return JsonResponse({"message": msg, "status": "COMPLETED"}, status=200)
    else:
        return JsonResponse({"error": msg, "status": "FAILED"}, status=400)


@require_GET
def api_payment_status(request, payment_id):
    try:
        payment = Payment.objects.select_related("booking").get(pk=payment_id)
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment record not found."}, status=404)

    return JsonResponse({
        "payment": {
            "id": payment.id,
            "booking_id": payment.booking.id,
            "amount": str(payment.amount),
            "phone_number": payment.phone_number,
            "status": payment.status,
            "mpesa_receipt_number": payment.mpesa_receipt_number,
            "created_at": payment.created_at.isoformat(),
        }
    }, status=200)
