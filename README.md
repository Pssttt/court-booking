# Court Booking WebApp

Professional, maintainable badminton court booking system with FastAPI.

## Quick Start

```bash
./start.sh
```

Open: **<http://localhost:8000>**

## How to Customize

### Edit Booking Data

Edit `config/settings.py`:

```python
BOOKING_DATA = {
    "phone": "YOUR_PHONE",
    "email": "YOUR_EMAIL",
    "student_code": "YOUR_STUDENT_ID",
    # ... etc
}
```

### Add/Remove Courts

Edit `config/settings.py`:

```python
COURTS = [
    {"id": "1", "name": "Court No. 1"},
    {"id": "2", "name": "Court No. 2"},
    # Add or remove as needed
]
```

### Change Default Submit Time

Edit `config/settings.py`:

```python
DEFAULT_SUBMIT_TIME = "13:00"  # Change to your preferred time
```

### Update Google Form Field IDs

If your Google Form changes, update `config/settings.py`:

```python
GOOGLE_FORM = {
    "submit_url": "https://...",
    "field_ids": {
        "name": "entry.XXXXXXX",  # Update these
        # ... etc
    }
}
```

## Project Structure

```
court-booking-webapp/
├── config/
│   ├── settings.py         # All configuration - EDIT HERE
│   └── __init__.py
├── app/
│   ├── services.py         # Form submission logic
│   ├── routes.py           # API endpoints
│   ├── templates.py        # HTML form
│   ├── models.py           # Data validation
│   └── __init__.py
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Dependencies
├── start.sh                # Quick start script
└── README.md              # This file
```

## Features

- ✅ Simple web form (3 names + court + time)
- ✅ Auto-fills all other data
- ✅ Scheduled submission (books at exact time)
- ✅ No Selenium (uses HTTP requests)
- ✅ Mobile friendly UI
- ✅ Easy to customize

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

### Check API docs

Visit: <http://localhost:8000/docs>

## Deployment

Works on any server (VPS, Heroku, Docker, etc.)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Booking form UI
- `POST /api/book` - Schedule a booking
- `GET /api/bookings` - List scheduled bookings
- `GET /api/courts` - Get available courts
- `GET /health` - Health check
- `GET /docs` - API documentation

## Customization Examples

### Change form appearance

Edit `app/templates.py` - modify CSS styles

### Add form validation

Edit `app/models.py` - add validators to BookingRequest

### Store bookings in database

Edit `app/routes.py` - replace in-memory list with database

### Add authentication

Edit `app/routes.py` - add FastAPI dependency

## Troubleshooting

### Port 8000 already in use

```bash
uvicorn main:app --port 8001
```

### Python version too old

Requires Python 3.9+

```bash
python3 --version
```

### Import errors

Reinstall dependencies:

```bash
pip install -r requirements.txt --force-reinstall
```

## Need Help?

All editable configuration is in `config/settings.py`

Key files:

- `config/settings.py` - Configuration & hardcoded data
- `app/services.py` - Form submission logic
- `app/routes.py` - API endpoints
- `app/templates.py` - HTML form

Clear comments in each file explain what does what.
