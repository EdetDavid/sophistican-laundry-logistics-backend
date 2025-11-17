from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import LaundryRequest, Driver
from .serializers import LaundryRequestSerializer, DriverSerializer
from utils.email_service import (
    notify_new_request,
    notify_request_status_update,
    notify_driver_assignment
)


class LaundryRequestViewSet(viewsets.ModelViewSet):
    # Use token authentication for request creation/updating so CSRF is not enforced
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LaundryRequestSerializer

    def get_queryset(self):
        user = self.request.user
        # Staff can see all requests, regular users only see their own
        if user.is_staff:
            return LaundryRequest.objects.all().order_by('-created_at')
        return LaundryRequest.objects.filter(customer=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Automatically set the customer to the current user
        request = serializer.save(customer=self.request.user)
        # Send email notifications
        notify_new_request(request)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        request_obj = self.get_object()
        driver_id = request.data.get('driver_id')
        if not driver_id:
            return Response({'detail': 'driver_id is required'}, status=400)
        try:
            driver = Driver.objects.get(pk=driver_id)
        except Driver.DoesNotExist:
            return Response({'detail': 'Driver not found'}, status=404)
        request_obj.driver = driver
        request_obj.status = 'assigned'
        request_obj.save()
        # Send email notifications
        notify_driver_assignment(request_obj)
        return Response(self.get_serializer(request_obj).data)
        
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update request status (driver only)"""
        laundry_request = self.get_object()
        old_status = laundry_request.status
        
        # Only assigned driver can update status
        if not request.user.is_staff and (not laundry_request.driver or laundry_request.driver.user != request.user):
            raise PermissionDenied("Only the assigned driver can update this request's status")
            
        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'status is required'}, status=400)
            
        # Validate status transition
        valid_transitions = {
            'assigned': ['picked_up', 'cancelled'],
            'picked_up': ['in_progress'],
            'in_progress': ['completed'],
        }
        
        if new_status not in valid_transitions.get(laundry_request.status, []):
            return Response(
                {'detail': f'Cannot transition from {laundry_request.status} to {new_status}'},
                status=400
            )
            
        laundry_request.status = new_status
        laundry_request.save()
        
        # Send status update notification
        notify_request_status_update(laundry_request, old_status)
        
        return Response(self.get_serializer(laundry_request).data)


class DriverViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DriverSerializer
    
    def get_queryset(self):
        # Admin sees all, drivers see only themselves
        user = self.request.user
        if user.is_staff:
            return Driver.objects.all()
        return Driver.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the authenticated driver's profile"""
        driver = get_object_or_404(Driver, user=request.user)
        serializer = self.get_serializer(driver)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get requests assigned to the authenticated driver"""
        driver = get_object_or_404(Driver, user=request.user)
        requests = LaundryRequest.objects.filter(driver=driver).order_by('-created_at')
        serializer = LaundryRequestSerializer(requests, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Update driver's current location and availability"""
        driver = get_object_or_404(Driver, user=request.user)
        serializer = DriverSerializer(driver, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def perform_create(self, serializer):
        # When creating a driver, link to current user for non-staff users.
        # Admins can create driver records without linking to themselves.
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Prevent creating more than one Driver record per non-staff user (OneToOne)
        if not request.user.is_staff and Driver.objects.filter(user=request.user).exists():
            return Response({'detail': 'A driver profile already exists for this user.'}, status=400)
        return super().create(request, *args, **kwargs)
