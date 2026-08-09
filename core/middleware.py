import re
import logging
from django.http import HttpResponseForbidden
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Common SQL Injection patterns
SQLI_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC|UNION|TRUNCATE)\b)",
    r"(--|\/\*|\*\/|@@|\bOR\b\s+['\"][^'\"']+=['\"])",
    r"('|\")\s*(\bOR\b|\bAND\b)\s*('|\")?\d+('|\")?\s*=\s*('|\")?\d+",
    r"(\bWAITFOR\s+DELAY\b|\bPG_SLEEP\b)",
]

# Common Cross-Site Scripting (XSS) patterns
XSS_PATTERNS = [
    r"(<script[^>]*>.*?</script>)",
    r"(javascript\s*:)",
    r"(onload\s*=)",
    r"(onerror\s*=)",
    r"(onclick\s*=)",
    r"(<iframe[^>]*>)",
    r"(<object[^>]*>)",
    r"(<embed[^>]*>)",
]

COMPILED_SQLI = [re.compile(p, re.IGNORECASE) for p in SQLI_PATTERNS]
COMPILED_XSS = [re.compile(p, re.IGNORECASE) for p in XSS_PATTERNS]


class WAFSecurityMiddleware:
    """
    Web Application Firewall (WAF) middleware inspecting all incoming requests
    for SQL Injection and Cross-Site Scripting (XSS) exploit vectors.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Inspect query parameters, raw body, and headers
        payloads_to_check = []

        for key, value in request.GET.items():
            payloads_to_check.append(f"{key}={value}")

        if request.content_type in ["application/x-www-form-urlencoded", "multipart/form-data"]:
            for key, value in request.POST.items():
                payloads_to_check.append(f"{key}={value}")

        query_string = request.META.get("QUERY_STRING", "")
        if query_string:
            payloads_to_check.append(query_string)

        full_payload = " ".join(payloads_to_check)

        # Check for SQL Injection threats
        for pattern in COMPILED_SQLI:
            if pattern.search(full_payload):
                logger.warning(f"WAF Blocked SQLi Attack Vector from IP {self._get_client_ip(request)}: {query_string}")
                return HttpResponseForbidden("Security Threat Detected: Request blocked by WAF.")

        # Check for XSS threats
        for pattern in COMPILED_XSS:
            if pattern.search(full_payload):
                logger.warning(f"WAF Blocked XSS Attack Vector from IP {self._get_client_ip(request)}: {query_string}")
                return HttpResponseForbidden("Security Threat Detected: Request blocked by WAF.")

        return self.get_response(request)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class RateLimitMiddleware:
    """
    Rate limiting middleware protecting endpoints against DoS / Brute-force attacks.
    Limits clients to max_requests per window_seconds.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = 120  # requests
        self.window_seconds = 60  # seconds

    def __call__(self, request):
        # Skip static assets
        if request.path.startswith("/static/"):
            return self.get_response(request)

        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit_{client_ip}"

        request_count = cache.get(cache_key, 0)
        if request_count >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")

        cache.set(cache_key, request_count + 1, timeout=self.window_seconds)
        return self.get_response(request)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class SecurityHeadersMiddleware:
    """
    Enforces HTTP security headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy (CSP)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:;"
        )
        response["Content-Security-Policy"] = csp
        return response
