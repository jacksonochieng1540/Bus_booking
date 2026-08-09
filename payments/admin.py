from django.contrib import admin
from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "amount",
        "phone_number",
        "mpesa_receipt_number",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "phone_number",
        "mpesa_receipt_number",
        "merchant_request_id",
        "checkout_request_id",
        "booking__passenger_name",
    )
