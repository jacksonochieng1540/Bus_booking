from django.urls import path
from bookings import views

app_name = "bookings"

urlpatterns = [
    path("create/<int:trip_id>/", views.create_booking, name="create_booking"),
    path("<int:pk>/", views.booking_detail, name="booking_detail"),
    path("<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
]
