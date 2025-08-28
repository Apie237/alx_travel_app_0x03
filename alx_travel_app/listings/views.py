from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Listing
from .serializers import ListingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(is_available=True)
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        listing = self.get_object()
        # Add availability logic here
        return Response({'available': listing.is_available})

# bookings/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Booking
from .serializers import BookingSerializer
from listings.tasks import send_booking_confirmation_email
from listings.models import Listing
import logging

logger = logging.getLogger(__name__)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(guest=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new booking and trigger email confirmation
        """
        try:
            # Validate listing exists
            listing_id = request.data.get('listing_id')
            if not listing_id:
                return Response(
                    {'error': 'listing_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                listing = Listing.objects.get(id=listing_id, is_available=True)
            except Listing.DoesNotExist:
                return Response(
                    {'error': 'Listing not found or not available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create booking
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            booking = serializer.save(guest=request.user)
            
            # Trigger email task asynchronously
            try:
                task = send_booking_confirmation_email.delay(
                    str(booking.id), 
                    request.user.id
                )
                logger.info(f'Email task triggered with ID: {task.id} for booking {booking.id}')
            except Exception as e:
                logger.error(f'Failed to trigger email task for booking {booking.id}: {str(e)}')
                # Don't fail the booking creation if email fails
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    'message': 'Booking created successfully. Confirmation email will be sent shortly.',
                    'booking': serializer.data
                }, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
            
        except Exception as e:
            logger.error(f'Error creating booking: {str(e)}')
            return Response(
                {'error': 'Failed to create booking'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a booking
        """
        booking = self.get_object()
        if booking.status == 'pending':
            booking.status = 'confirmed'
            booking.save()
            return Response({'message': 'Booking confirmed successfully'})
        return Response(
            {'error': 'Booking cannot be confirmed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking
        """
        booking = self.get_object()
        if booking.status in ['pending', 'confirmed']:
            booking.status = 'cancelled'
            booking.save()
            return Response({'message': 'Booking cancelled successfully'})
        return Response(
            {'error': 'Booking cannot be cancelled'}, 
            status=status.HTTP_400_BAD_REQUEST
        )