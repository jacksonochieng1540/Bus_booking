# SafariSacco 🚌 - Bus & Coach Booking System

[![CI Workflow](https://github.com/jacksonochieng1540/Bus_booking/actions/workflows/ci.yml/badge.svg)](https://github.com/jacksonochieng1540/Bus_booking/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0+](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Svelte](https://img.shields.io/badge/frontend-Svelte%20SPA-orange.svg)](https://svelte.dev/)
[![Docker](https://img.shields.io/badge/containerized-Docker-blue.svg)](https://www.docker.com/)

**SafariSacco** is a production-ready, high-performance Kenyan bus and coach booking platform. Built with a Django 5 REST backend and a modern Svelte Single-Page Application (SPA) frontend, it features automated Safaricom M-Pesa STK push payments, async Celery/Redis SMS ticket dispatches, Google OAuth authentication, Web Application Firewall (WAF) exploit protection, and Render.com deployment automation.

---

## 🌟 Key Features

* **Svelte Single-Page Application (SPA)**:
  * Interactive Journey Planner widget with city swap controls (`⇄`) and one-way / round-trip selectors.
  * Real-time express departure cards with live available seat counters and fare pricing in KES.
  * Interactive coach seat grid mapping color-coded seats (Green: Available, Amber: Pending, Red: Occupied).
  * Floating WhatsApp Customer Service chat integration (`wa.me/254712345678`).

* **Strict Database Double-Booking Prevention**:
  * Enforces a database-level `UniqueConstraint(fields=['trip', 'seat_number'], name='unique_trip_seat')` on the `Booking` model to eliminate race-condition seat conflicts.

* **M-Pesa Mobile Payments & Webhook Security**:
  * Safaricom M-Pesa STK Push simulation and transaction status polling.
  * Webhook callback signature verification (`verify_webhook_signature`) using HMAC SHA256 hashing and token authentication.

* **Async Celery & Redis Queue**:
  * Asynchronous dispatching of passenger SMS booking confirmations (`async_send_booking_confirmation`).

* **Web Application Firewall (WAF) & Exploit Protection**:
  * Built-in `WAFSecurityMiddleware` scanning request parameters, body, and query strings for SQL Injection (`UNION SELECT`, `' OR 1=1`, `DROP`) and XSS attacks.
  * `RateLimitMiddleware` guarding against DoS and brute-force attempts.
  * Hardened HTTP security headers (`Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `HSTS`).

* **Cloudflare CDN & Dual Database Engine**:
  * Static file CDN resolution (`CDN_URL`) with WhiteNoise asset caching.
  * Automatic PostgreSQL connection in production (`DATABASE_URL`) with seamless SQLite fallback for local development.

---

## 🏗️ Project Architecture

```
Bus_project/
├── sacco_booking/         # Django Core Configuration & Celery App
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
├── fleets/                # Buses, Routes, and Express Trips
├── bookings/              # Seat Reservations & Unique Constraint Models
├── payments/              # M-Pesa STK Push & Webhook Verification
├── notifications/         # SMS Audit Logs & Async Celery Tasks
├── core/                  # Authentication, Google OAuth, & WAF Security Middlewares
├── frontend/              # Svelte Single-Page Application (Vite + Svelte)
│   ├── src/
│   │   ├── lib/           # Svelte Components (Navbar, SeatMap, JourneyPlanner, etc.)
│   │   └── App.svelte
│   └── vite.config.js
├── nginx/                 # Nginx Edge Proxy & CDN Asset Caching Config
│   ├── default.conf
│   └── Dockerfile
├── render.yaml            # Render.com Infrastructure as Code Deployment Spec
├── Dockerfile             # Multi-stage Django Container Build
├── docker-compose.yml     # Orchestration (Web + Nginx + Redis + Celery)
└── requirements.txt       # Production Dependencies
```

---

## ⚡ Quick Start & Local Development

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Redis (optional for local Celery async task execution)

### 2. Backend Setup (Django)
```bash
# Clone the repository
git clone https://github.com/jacksonochieng1540/Bus_booking.git
cd Bus_booking

# Create virtual environment & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations & seed sample express departures
python manage.py migrate
python manage.py seed_data

# Run Django backend server
python manage.py runserver 8000
```

### 3. Frontend Setup (Svelte SPA)
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Svelte Vite development server (proxies API calls to Django on port 8000)
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🌐 Production Deployment (Render.com)

This repository includes a complete [render.yaml](file:///home/notoriousmma/Documents/Bus_project/render.yaml) specification:

1. Connect your GitHub repository to **Render.com**.
2. Render automatically provisions:
   - **Web Service**: Gunicorn WSGI + Django application with automatic migration and static asset compilation.
   - **PostgreSQL Database**: Managed relational database.
   - **Redis Service**: Message broker for Celery worker.
   - **Celery Worker**: Asynchronous task processor.

---

## 🔌 REST API Endpoints

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Fleets** | `GET` | `/api/v1/routes/` | List all available routes & fare prices |
| **Fleets** | `GET` | `/api/v1/trips/` | List upcoming bus departures & seat availability |
| **Fleets** | `GET` | `/api/v1/trips/<id>/` | Detailed trip info & interactive seat grid layout |
| **Bookings**| `POST`| `/bookings/api/v1/create/<trip_id>/` | Reserve passenger seat number |
| **Bookings**| `GET` | `/bookings/api/v1/detail/<id>/` | Retrieve reservation details & ticket receipt |
| **Payments**| `POST`| `/payments/api/v1/stk-push/` | Initiate M-Pesa STK Push prompt |
| **Payments**| `POST`| `/payments/api/v1/callback/<id>/` | Secure HMAC Webhook payment callback |
| **Accounts**| `POST`| `/accounts/api/v1/login/` | Passenger authentication |
| **Accounts**| `POST`| `/accounts/api/v1/register/` | Passenger registration |

---

## 🧪 Testing & Quality Assurance

Run the comprehensive Django backend test suite (24 tests covering models, forms, APIs, and WAF security exploit prevention):

```bash
python manage.py test core fleets bookings payments notifications
```

Test Svelte production compilation:
```bash
cd frontend && npm run build
```

Run Python code linter:
```bash
flake8 .
```

---

## 📄 License
Licensed under the [MIT License](LICENSE). &copy; 2026 SafariSacco Kenya Ltd.
