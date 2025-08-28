from django.core.management.base import BaseCommand
from listings.tasks import send_booking_confirmation_email
from django.contrib.auth.models import User
from bookings.models import Booking

class Command(BaseCommand):
    help = 'Test Celery email task'
    
    def handle(self, *args, **options):
        # Get a test booking
        try:
            booking = Booking.objects.first()
            if booking:
                task = send_booking_confirmation_email.delay(str(booking.id), booking.guest.id)
                self.stdout.write(
                    self.style.SUCCESS(f'Test email task triggered: {task.id}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No bookings found. Create a booking first.')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )