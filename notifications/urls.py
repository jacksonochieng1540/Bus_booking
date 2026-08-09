from django.urls import path
from notifications import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="notification_list"),
]
