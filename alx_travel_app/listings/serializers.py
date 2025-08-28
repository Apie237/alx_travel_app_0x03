from rest_framework import serializers
from .models import Listing
from django.contrib.auth.models import User

class ListingSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'host']
    
    def create(self, validated_data):
        validated_data['host'] = self.context['request'].user
        return super().create(validated_data)

# bookings/serializers.py
from rest_framework import serializers
from .models import Booking
from listings.serializers import ListingSerializer

class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)
    guest = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'guest', 'total_price']
    
    def validate(self, data):
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        
        return data
    
    def create(self, validated_data):
        validated_data['guest'] = self.context['request'].user
        return super().create(validated_data)