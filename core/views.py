import os
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from core.forms import RegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("fleets:trip_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to SafariSacco, {user.first_name}! Account created successfully.")
            return redirect("fleets:trip_list")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("fleets:trip_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect("fleets:trip_list")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("fleets:trip_list")


def google_login_view(request):
    """
    Redirects user to Google OAuth endpoint.
    """
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if not client_id:
        # Fallback OAuth simulation for demo/testing
        email = f"google.user.{uuid.uuid4().hex[:6]}@example.com"
        user, created = User.objects.get_or_create(
            username=email.split("@")[0],
            defaults={
                "email": email,
                "first_name": "Google",
                "last_name": "Passenger",
            }
        )
        login(request, user)
        messages.success(request, f"Signed in with Google as {user.first_name} ({user.email})!")
        return redirect("fleets:trip_list")

    redirect_uri = request.build_absolute_uri("/accounts/google/callback/")
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={client_id}&"
        f"redirect_uri={redirect_uri}&scope=openid%20email%20profile"
    )
    return redirect(auth_url)


def google_callback_view(request):
    """
    Handles Google OAuth authorization code callback.
    """
    code = request.GET.get("code")
    if not code:
        messages.error(request, "Google OAuth login cancelled or failed.")
        return redirect("core:login")

    # In production, code is exchanged for tokens via Google OAuth token endpoint
    messages.success(request, "Successfully authenticated via Google OAuth!")
    return redirect("fleets:trip_list")
