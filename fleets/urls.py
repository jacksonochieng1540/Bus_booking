from django.urls import path
from fleets import views, api_views

app_name = "fleets"

urlpatterns = [
    path("", views.trip_list, name="trip_list"),
    path("trip/<int:pk>/", views.trip_detail, name="trip_detail"),
    # API v1 endpoints
    path("api/v1/routes/", api_views.api_route_list, name="api_route_list"),
    path("api/v1/trips/", api_views.api_trip_list, name="api_trip_list"),
    path("api/v1/trips/<int:pk>/", api_views.api_trip_detail, name="api_trip_detail"),
]
