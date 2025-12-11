# Court Booking WebApp

Professional, maintainable badminton court booking system with FastAPI.

## Quick Start

1.  **Configure Environment**:
    Copy `.env.example` to `.env` and fill in your details:
    ```bash
    cp .env.example .env
    ```

2.  **Start the Server**:
    ```bash
    ./start.sh
    ```

3.  **Open Application**:
    Go to **<http://localhost:3000>**

## Configuration (.env)

The application is configured via environment variables. Key settings include:

-   **Booking Data**: Your personal details (Name, Phone, Student ID, etc.) for the form.
-   **Google Form**: The URL and Field IDs for the target Google Form.
-   **Security**:
    -   `CANCEL_PASSWORD`: Master password to cancel any booking.
    -   `DISCORD_WEBHOOK_URL`: (Optional) Webhook URL for receiving cancellation OTPs.
-   **Server**: Host and port settings.

## Project Structure

```
court-booking-webapp/
├── app/
│   ├── discord_service.py  # Discord OTP logic
│   ├── email_service.py    # Email notification logic
│   ├── models.py           # Data validation (Pydantic)
│   ├── routes.py           # API endpoints
│   ├── services.py         # Form submission logic
│   ├── storage.py          # JSON file storage
│   ├── static/             # CSS, Icons
│   └── templates/          # HTML templates
├── config/
│   └── settings.py         # Configuration loader
├── data/                   # Stored bookings (JSON)
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Dependencies
├── start.sh                # Quick start script
└── README.md               # This file
```

## Features

-   ✅ **Modern UI**: Clean, card-based layout with mobile responsiveness.
-   ✅ **Resilient Booking**: Schedules bookings to submit at the exact required time.
-   ✅ **Security**:
    -   Discord OTP integration for secure booking cancellation.
    -   Master password override.
    -   Input sanitization (XSS prevention).
-   ✅ **Validation**:
    -   Real-time client-side form validation.
    -   Strict server-side data validation.
    -   Duplicate booking prevention.
-   ✅ **No Headless Browser**: Uses efficient HTTP requests (faster & more reliable than Selenium).

## API Endpoints

-   `GET /` - Booking form UI
-   `GET /bookings` - Dashboard of all bookings
-   `POST /api/book` - Schedule a new booking
-   `DELETE /api/cancel` - Cancel a booking (requires Password/OTP)
-   `POST /api/request-cancel-code` - Request cancellation OTP via Discord
-   `GET /api/bookings` - List API
-   `GET /api/courts` - Get available courts

## Development

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run with auto-reload

```bash
uvicorn main:app --reload
```

## Troubleshooting

### Port 8000 already in use
Edit `.env` or run:
```bash
uvicorn main:app --port 8001
```

### Discord OTP not working
Ensure `DISCORD_WEBHOOK_URL` is set correctly in your `.env` file.