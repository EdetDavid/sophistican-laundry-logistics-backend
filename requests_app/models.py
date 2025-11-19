from django.db import models
from django.conf import settings


class Driver(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_available = models.BooleanField(default=True)
    last_location_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LaundryRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("picked_up", "Picked Up"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ("shirt_ironing", "Shirt Ironing"),
        ("trousers_ironing", "Trousers Ironing"),
        ("full_ironing", "Full Ironing Service"),
        ("suits", "Suit Cleaning & Pressing"),
        ("full_home_service", "Full Home Service"),
        ("wash_dry", "Wash & Dry"),
        ("hand_wash", "Hand Wash"),
        ("dry_clean", "Dry Clean"),
        ("special_care", "Special Care (Delicates)"),
        ("other", "Other"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests"
    )
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField()
    pickup_time = models.DateTimeField(null=True, blank=True)
    items_description = models.TextField(blank=True)
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPE_CHOICES, default="full_home_service")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_name} - {self.status}"
