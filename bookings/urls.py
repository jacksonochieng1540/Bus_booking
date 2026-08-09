from django.urls import path
from bookings import views, api_views

app_name = "bookings"

urlpatterns = [
    path("create/<int:trip_id>/", views.create_booking, name="create_booking"),
    path("<int:pk>/", views.booking_detail, name="booking_detail"),
    path("<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
    # API v1 endpoints
    path("api/v1/create/<int:trip_id>/", api_views.api_create_booking, name="api_create_booking"),
    path("api/v1/<int:pk>/", api_views.api_booking_detail, name="api_booking_detail"),
    path("api/v1/<int:pk>/cancel/", api_views.api_booking_cancel, name="api_booking_cancel"),
]
