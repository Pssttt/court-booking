# Development Guide

## Project Overview

Court Booking WebApp is a FastAPI application that auto-fills and submits Google Forms for badminton court reservations at scheduled times.

**Tech Stack:**

- Backend: FastAPI + Uvicorn
- Frontend: HTML/CSS/JavaScript (vanilla)
- Storage: JSON file (`data/bookings.json`)
- Email: Resend API
- Form Submission: HTTP POST to Google Forms

## Setup

### 1. Install Dependencies

```bash
cd court-booking-webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your values.

### 3. Get Google Form Field IDs

Extract `entry.XXXXX` IDs from your Google Form:

1. Open your Google Form
2. Press F12 → Network tab
3. Fill and submit the form
4. Find `formResponse` request
5. Check Request body for `entry.XXXXXX` values
6. Update `config/settings.py` field_ids

### 4. Start Server

```bash
./start.sh
```

Visit: `http://localhost:8000`

## Project Structure

```
court-booking-webapp/
├── main.py                 # FastAPI entry point
├── config/
│   └── settings.py         # Configuration & env variables
├── app/
│   ├── models.py           # Data models (Pydantic)
│   ├── routes.py           # API endpoints
│   ├── services.py         # Form submission logic
│   ├── storage.py          # JSON persistence
│   ├── email_service.py    # Email via Resend
│   └── templates.py        # HTML form
├── data/
│   └── bookings.json       # Stored bookings (auto-created)
├── docs/
│   ├── DEVELOPMENT.md      # This file
│   └── DEPLOYMENT.md       # Production guide
├── requirements.txt        # Dependencies
├── .env.example            # Secrets
└── .gitignore
```

## Key Files

### config/settings.py

Main configuration:

- Booking data (phone, email, student ID)
- Court options
- Google Form URLs & field IDs
- Email settings
- Server settings

### app/services.py

Form submission:

- `submit_form()` - Submits to Google Form
- `wait_until_and_submit()` - Schedules submission at time

### app/routes.py

API endpoints:

- `POST /api/book` - Schedule booking
- `GET /api/bookings` - List bookings
- `GET /api/courts` - Available courts

### app/storage.py

JSON persistence:

- `add_booking()` - Save booking
- `load_bookings()` - Load from JSON
- `get_all_bookings()` - Get all stored

### app/email_service.py

Email sending:

- `send_confirmation_email()` - Send via Resend

## API Endpoints

### Book a Court

```bash
POST /api/book

{
  "p1": "Player 1",
  "p2": "Player 2",
  "p3": "Player 3",
  "court": "Court No. 3",
  "submit_time": "13:00",
  "confirmation_email": "me@psstee.dev"  # Optional
}
```

### Get Bookings

```bash
GET /api/bookings
```

### Get Courts

```bash
GET /api/courts
```

## Features

- **Scheduled Booking**: Auto-submit at specific time
- **Auto-Fill**: Pre-fill phone, email, student ID
- **JSON Storage**: Persistent bookings
- **Email Confirmations**: Optional user emails
- **Multi-Page Forms**: Handles 4-page Google Forms

## Configuration

### Change Submission Time

Edit `config/settings.py`:

```python
DEFAULT_SUBMIT_TIME = "14:30"
```

### Add Courts

```python
COURTS = [
    {"id": "1", "name": "Court No. 1"},
    {"id": "2", "name": "Court No. 2"},
    # Add more...
]
```

### Customize Email

Edit `app/email_service.py` - modify HTML template in `send_confirmation_email()`

## Troubleshooting

| Issue               | Solution                                        |
| ------------------- | ----------------------------------------------- |
| Form submission 400 | Check field IDs, run `debug_form.py`            |
| Email not sending   | Verify `RESEND_API_KEY` in `.env`               |
| Server won't start  | Install deps: `pip install -r requirements.txt` |
| Bookings lost       | Check `data/` folder exists and is writable     |

## Testing

### Test Locally

```bash
./start.sh
```

### Test API

```bash
curl -X POST http://localhost:8000/api/book \
  -H "Content-Type: application/json" \
  -d '{"p1":"John","p2":"Jane","p3":"Bob","court":"Court No. 1","submit_time":"13:05"}'
```

### View Bookings

```bash
curl http://localhost:8000/api/bookings
```

## Code Style

- Type annotations required
- Minimal comments (only complex logic)
- Descriptive names
- PEP 8 conventions

## Future Upgrades

- **Storage**: JSON → PostgreSQL for production
- **Auth**: User accounts & login
- **Features**: Recurring bookings, cancellation, dashboard

## Security

- Never commit `.env`
- Keep API keys private
- Use environment variables for secrets
- Validate all user input
- Use HTTPS in production

## Support

Debug logs:

```
2025-12-09 13:35:00 - app.services - INFO - Submitting form
2025-12-09 13:35:01 - app.services - INFO - Form submitted successfully
```

Check logs for errors and email confirmations.

## License

MIT License
