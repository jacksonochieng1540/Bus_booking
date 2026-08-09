from django.urls import path
from payments import views, api_views

app_name = "payments"

urlpatterns = [
    path("initiate/<int:booking_id>/", views.initiate_payment, name="initiate_payment"),
    path("status/<int:payment_id>/", views.payment_status, name="payment_status"),
    path("callback/<int:payment_id>/", views.simulate_callback, name="simulate_callback"),
    # API v1 endpoints
    path("api/v1/stk-push/", api_views.api_initiate_payment, name="api_initiate_payment"),
    path("api/v1/callback/<int:payment_id>/", api_views.api_payment_callback, name="api_payment_callback"),
    path("api/v1/status/<int:payment_id>/", api_views.api_payment_status, name="api_payment_status"),
]
