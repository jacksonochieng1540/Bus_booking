from django.urls import path
from fleets import views

app_name = "fleets"

urlpatterns = [
    path("", views.trip_list, name="trip_list"),
    path("trip/<int:pk>/", views.trip_detail, name="trip_detail"),
]
