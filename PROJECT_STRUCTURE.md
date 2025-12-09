# ourt Booking WebApp

Production-ready project structure. Easy to maintain and extend.

## Project Structure

```
court-booking-webapp/
│
├── config/                # Configuration - EDIT HERE
│   ├── __init__.py
│   └── settings.py        # All settings in one place
│
├── app/                   # Application code
│   ├── __init__.py
│   ├── services.py        # Form submission logic
│   ├── routes.py          # API endpoints
│   ├── templates.py       # HTML form
│   └── models.py          # Data validation
│
├── docs/                  # Documentation
│   ├── DEVELOPMENT.md     # How to customize
│   └── DEPLOYMENT.md      # How to deploy
│
├── main.py                # FastAPI entry point
├── verify.py              # Verify configuration
├── requirements.txt       # Python dependencies
├── start.sh               # Quick start script
└── README.md              # Quick reference
```

## Key Features

- Config: `config/settings.py`
- Logic: `app/services.py`
- API: `app/routes.py`
- UI: `app/templates.py`

- All config in one file (`config/settings.py`)
- Clear comments explaining each setting
- Add courts, change data, update URLs easily

- Type hints on functions
- Proper error handling
- Logging throughout
- Input validation

## Quick Start

```bash
./start.sh
```

Open: <http://localhost:8000>

## What To Edit

### Change booking data

→ Edit `config/settings.py` → `BOOKING_DATA`

### Add more courts

→ Edit `config/settings.py` → `COURTS`

### Change default submit time

→ Edit `config/settings.py` → `DEFAULT_SUBMIT_TIME`

### Update Google Form IDs

→ Edit `config/settings.py` → `GOOGLE_FORM`

### Customize form appearance

→ Edit `app/templates.py` → CSS styles

### Add form validation

→ Edit `app/models.py` → Add validators

### Modify submission logic

→ Edit `app/services.py` → `submit_form()` function

### Add API endpoints

→ Edit `app/routes.py` → Add `@router.post()` or `@router.get()`

## File Organization by Purpose

### If you want to

**Change which courts are available**
→ `config/settings.py` (COURTS)

**Change the form HTML/CSS**
→ `app/templates.py` (get_booking_form_html function)

**Fix form submission issues**
→ `app/services.py` (submit_form function)

**Add new API endpoint**
→ `app/routes.py` (add @router.post() or @router.get())

**Change validation rules**
→ `app/models.py` (BookingRequest class)

**Add custom logic**
→ `app/services.py` (new functions)

## Testing

Test API:

```bash
curl -X POST http://localhost:8000/api/book \
  -H "Content-Type: application/json" \
  -d '{"p1":"Name1","p2":"Name2","p3":"Name3","court":"Court No. 1 (in thai)"}'
```

## Deployment

Local:

```bash
./start.sh
```

Production:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

See docs/DEPLOYMENT.md for:

- VPS deployment
- Docker deployment
- Heroku deployment
- Railway deployment
- SSL/HTTPS setup

## Development

See docs/DEVELOPMENT.md for:

- File organization details
- How to make changes
- Testing approaches
- Error handling
- Security best practices
- Performance optimization

### Add database persistence

```python
# Install: pip install sqlalchemy
# In app/models.py, add SQLAlchemy models
# In app/routes.py, save bookings to database instead of memory
```

### Add authentication

```python
# In app/routes.py
from fastapi.security import HTTPBearer

@router.post("/api/book")
async def create_booking(
    booking: BookingRequest,
    credentials = Depends(HTTPBearer())
):
    # Verify user before booking
```

### Add court availability checking

```python
# In app/services.py
def check_court_available(court, time):
    # Query database to check if court is available
```

## Performance Notes

- Form submission happens in background (non-blocking)
- Users get immediate response
- Actual submission to Google Forms happens later
- Multiple bookings can be scheduled simultaneously

## Security Notes

Current setup is for **personal/team use**.

For production with sensitive data, add:

1. Authentication (see DEVELOPMENT.md)
2. Environment variables for secrets
3. HTTPS/SSL
4. Rate limiting
5. Input validation

## Support

Most common edits are in `config/settings.py`:

- Change phone/email
- Add/remove courts
- Update Google Form URLs

For deeper changes, see:

- `docs/DEVELOPMENT.md` - Customization guide
- `docs/DEPLOYMENT.md` - Deployment guide
- Code comments - Explain each component
