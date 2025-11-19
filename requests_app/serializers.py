from rest_framework import serializers
from .models import LaundryRequest, Driver
from django.contrib.auth import get_user_model

User = get_user_model()

class DriverSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = Driver
        fields = [
            'id', 'name', 'phone', 'email', 'first_name', 'last_name',
            'latitude', 'longitude', 'is_available', 'last_location_update'
        ]
        read_only_fields = ['user', 'last_location_update']


class LaundryRequestSerializer(serializers.ModelSerializer):
    # The driver field will be null if no driver is assigned. If present, it includes id, name, phone, email, first_name, last_name, latitude, longitude, is_available, last_location_update.
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(), source='driver', write_only=True, required=False
    )
    customer_email = serializers.EmailField(source='customer.email', read_only=True)

    class Meta:
        model = LaundryRequest
        fields = [
            'id', 'customer_name', 'customer_email', 'phone', 'address', 'pickup_time', 
            'items_description', 'service_type', 'status', 'driver', 'driver_id', 'created_at', 'updated_at',
        ]
        read_only_fields = ['customer_email']
