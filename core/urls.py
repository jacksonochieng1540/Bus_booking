from django.urls import path
from core import views, api_views

app_name = "core"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("google/", views.google_login_view, name="google_login"),
    path("google/callback/", views.google_callback_view, name="google_callback"),
    # API v1 endpoints
    path("api/v1/register/", api_views.api_register, name="api_register"),
    path("api/v1/login/", api_views.api_login, name="api_login"),
]
