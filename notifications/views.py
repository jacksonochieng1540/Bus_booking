from django.shortcuts import render
from notifications.models import NotificationLog


def notification_list(view_request):
    notifications = NotificationLog.objects.select_related("booking").order_by("-created_at")[:50]
    return render(
        view_request,
        "notifications/notification_list.html",
        {"notifications": notifications},
    )
