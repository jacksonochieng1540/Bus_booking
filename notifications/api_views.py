from django.http import JsonResponse
from django.views.decorators.http import require_GET
from notifications.models import NotificationLog


@require_GET
def api_notification_list(request):
    logs = NotificationLog.objects.select_related("booking").order_by("-created_at")[:50]
    data = [
        {
            "id": log.id,
            "booking_id": log.booking.id if log.booking else None,
            "recipient": log.recipient,
            "message": log.message,
            "status": log.status,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
    return JsonResponse({"notifications": data}, status=200)
