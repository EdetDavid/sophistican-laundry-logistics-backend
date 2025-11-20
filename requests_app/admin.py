from django.contrib import admin
from .models import LaundryRequest, Driver
from .models import PricingItem

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'phone', 'is_available', 'last_location_update')
    list_filter = ('is_available',)
    search_fields = ('name', 'phone', 'user__email')
    raw_id_fields = ('user',)
    list_editable = ('is_available',)
    date_hierarchy = 'last_location_update'

@admin.register(LaundryRequest)
class LaundryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer', 'status', 'driver', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'phone', 'address', 'customer__email')
    raw_id_fields = ('customer', 'driver')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'phone', 'address')
        }),
        ('Request Details', {
            'fields': ('items_description', 'pickup_time', 'status', 'driver')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PricingItem)
class PricingItemAdmin(admin.ModelAdmin):
    list_display = ('slug', 'label', 'price', 'ordering')
    list_editable = ('price', 'ordering')
    search_fields = ('slug', 'label')
    ordering = ('ordering', 'slug')
    list_per_page = 50