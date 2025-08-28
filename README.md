# ALX Travel App 0x03 - Background Task Management with Celery

## Project Overview

This Django application implements background task management using Celery with Redis as a message broker to handle asynchronous email notifications for travel booking confirmations.

## Features

- **Background Email Processing**: Asynchronous email notifications using Celery
- **Booking Management**: REST API for creating and managing travel bookings
- **Email Notifications**: Automatic booking confirmation emails sent via background tasks
- **Celery Integration**: Configured with Redis broker for reliable task processing
- **Error Handling**: Task retry mechanisms with exponential backoff

## Architecture

- **Django 4.2.7**: Web framework
- **Django REST Framework**: API development
- **Celery 5.3.4**: Distributed task queue
- **Redis**: Message broker and result backend
- **Email Backend**: Configurable email service integration

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd alx_travel_app_0x03

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start Services

```bash
# Start Redis server
redis-server

# Start Celery worker (new terminal)
celery -A alx_travel_app worker --loglevel=info

# Start Django server (new terminal)
python manage.py runserver
```

## API Endpoints

### Bookings
- `POST /api/bookings/` - Create booking (triggers email task)
- `GET /api/bookings/` - List user bookings
- `GET /api/bookings/{id}/` - Get booking details

### Listings
- `GET /api/listings/` - List available properties
- `POST /api/listings/` - Create new listing

## Celery Tasks

### Email Confirmation Task
Located in `listings/tasks.py`:

```python
@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id, user_id):
    # Sends booking confirmation email asynchronously
    # Includes retry logic and error handling
```

### Task Features
- **Automatic Retries**: Up to 3 retry attempts
- **Error Logging**: Comprehensive logging for debugging
- **Email Templates**: HTML and plain text email formats
- **Rate Limiting**: Configurable task rate limits

## Configuration

### Celery Settings
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### Email Configuration
- **Development**: Console backend (prints to terminal)
- **Production**: SMTP backend with configurable providers

## Testing

### Test Booking Creation
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "uuid-here",
    "check_in_date": "2024-12-01",
    "check_out_date": "2024-12-05",
    "guests_count": 2
  }'
```

### Monitor Celery Tasks
```bash
# Check active tasks
celery -A alx_travel_app inspect active

# Monitor task events
celery -A alx_travel_app events
```

## Project Structure

```
alx_travel_app_0x03/
├── README.md
├── requirements.txt
├── manage.py
└── alx_travel_app/
    ├── __init__.py
    ├── settings.py
    ├── celery.py
    ├── urls.py
    ├── wsgi.py
    ├── listings/
    │   ├── tasks.py          # Celery email tasks
    │   ├── views.py          # BookingViewSet with email trigger
    │   └── models.py
    └── bookings/
        ├── models.py
        ├── views.py
        └── serializers.py
```

## Key Implementation Details

### Email Task Trigger
The `BookingViewSet.create()` method triggers the email task:

```python
def create(self, request, *args, **kwargs):
    # Create booking
    booking = serializer.save(guest=request.user)
    
    # Trigger async email task
    send_booking_confirmation_email.delay(
        str(booking.id), 
        request.user.id
    )
```

### Background Task Processing
- Tasks are processed by Celery workers
- Redis handles message queuing
- Email failures don't affect booking creation
- Retry logic handles temporary failures

## Monitoring

### Flower Web Interface
```bash
pip install flower
celery -A alx_travel_app flower
# Access at http://localhost:5555
```

### Task Monitoring Commands
```bash
# Worker status
celery -A alx_travel_app inspect stats

# Task history
celery -A alx_travel_app inspect registered
```

## Deployment Notes

- Use RabbitMQ for production environments
- Configure proper email service (SendGrid, SES)
- Set up process management (systemd, supervisor)
- Use environment variables for sensitive settings
- Implement proper logging and monitoring

## Troubleshooting

### Common Issues
1. **Redis connection failed**: Ensure Redis server is running
2. **Tasks not executing**: Check Celery worker is active
3. **Emails not sending**: Verify email backend configuration

### Debug Commands
```bash
# Test Redis connection
redis-cli ping

# Check Celery worker logs
celery -A alx_travel_app worker --loglevel=debug

# Test email task manually
python manage.py shell
>>> from listings.tasks import send_booking_confirmation_email
>>> task = send_booking_confirmation_email.delay('test-id', 1)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the ALX Software Engineering program.

---

**Author**: ALX Student  
**Project**: Background Task Management with Celery  
**Version**: 0x03