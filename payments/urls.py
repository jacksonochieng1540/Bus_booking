from django.urls import path
from payments import views

app_name = "payments"

urlpatterns = [
    path("initiate/<int:booking_id>/", views.initiate_payment, name="initiate_payment"),
    path("status/<int:payment_id>/", views.payment_status, name="payment_status"),
    path("callback/<int:payment_id>/", views.simulate_callback, name="simulate_callback"),
]
