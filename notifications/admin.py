from django.contrib import admin
from notifications.models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "recipient", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("recipient", "message", "booking__passenger_name")
