import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from core.forms import RegistrationForm


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
    except Exception:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    form = RegistrationForm(data)
    if form.is_valid():
        user = form.save()
        return JsonResponse({
            "message": "User registered successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=201)
    else:
        return JsonResponse({"errors": form.errors}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
    except Exception:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"error": "Username and password are required."}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=200)
    else:
        return JsonResponse({"error": "Invalid credentials."}, status=401)
