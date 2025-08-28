from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id, user_id):
    """
    Send booking confirmation email asynchronously
    """
    try:
        # Import here to avoid circular imports
        from bookings.models import Booking
        
        # Get booking and user objects
        booking = Booking.objects.select_related('listing', 'guest').get(id=booking_id)
        user = User.objects.get(id=user_id)
        
        # Prepare email context
        context = {
            'user': user,
            'booking': booking,
            'listing': booking.listing,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }
        
        # Render email content
        subject = f'Booking Confirmation - {booking.listing.title}'
        html_message = render_to_string('emails/booking_confirmation.html', context)
        plain_message = render_to_string('emails/booking_confirmation.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Booking confirmation email sent successfully for booking {booking_id}')
        return f'Email sent successfully to {user.email}'
        
    except Booking.DoesNotExist:
        logger.error(f'Booking with id {booking_id} does not exist')
        raise
    except User.DoesNotExist:
        logger.error(f'User with id {user_id} does not exist')
        raise
    except Exception as exc:
        logger.error(f'Error sending booking confirmation email: {str(exc)}')
        # Retry the task
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@shared_task
def send_booking_reminder_email(booking_id):
    """
    Send booking reminder email
    """
    try:
        from bookings.models import Booking
        
        booking = Booking.objects.select_related('listing', 'guest').get(id=booking_id)
        
        context = {
            'user': booking.guest,
            'booking': booking,
            'listing': booking.listing,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }
        
        subject = f'Booking Reminder - {booking.listing.title}'
        html_message = render_to_string('emails/booking_reminder.html', context)
        plain_message = render_to_string('emails/booking_reminder.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.guest.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Booking reminder email sent for booking {booking_id}')
        return f'Reminder email sent successfully'
        
    except Exception as exc:
        logger.error(f'Error sending booking reminder email: {str(exc)}')
        raise

@shared_task
def cleanup_expired_bookings():
    """
    Clean up expired pending bookings
    """
    from django.utils import timezone
    from datetime import timedelta
    from bookings.models import Booking
    
    try:
        # Delete pending bookings older than 24 hours
        expired_time = timezone.now() - timedelta(hours=24)
        expired_bookings = Booking.objects.filter(
            status='pending',
            created_at__lt=expired_time
        )
        
        count = expired_bookings.count()
        expired_bookings.delete()
        
        logger.info(f'Cleaned up {count} expired bookings')
        return f'Cleaned up {count} expired bookings'
        
    except Exception as exc:
        logger.error(f'Error cleaning up expired bookings: {str(exc)}')
        raise