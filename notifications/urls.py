from django.urls import path
from notifications import views, api_views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="notification_list"),
    # API v1 endpoints
    path("api/v1/", api_views.api_notification_list, name="api_notification_list"),
]
