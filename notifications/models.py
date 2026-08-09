from django.db import models


class NotificationLog(models.Model):
    class Status(models.TextChoices):
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    recipient = models.CharField(max_length=100)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.SENT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.recipient} ({self.status}) at {self.created_at}"
