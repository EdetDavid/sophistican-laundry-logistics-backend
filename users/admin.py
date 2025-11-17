from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.conf import settings

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('profile_image_tag', 'email', 'first_name', 'mobile_number', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'mobile_number')
    ordering = ('-date_joined',)

    def profile_image_tag(self, obj):
        # Prefer the uploaded image if available, otherwise point to the
        # default profile picture under MEDIA_URL.
        try:
            if obj.profile_picture:
                url = obj.profile_picture.url
            else:
                url = settings.MEDIA_URL + 'profile_pics/default.png'
            return format_html('<img src="{}" width="48" style="border-radius:50%; object-fit:cover;" />', url)
        except Exception:
            return ''

    profile_image_tag.short_description = 'Picture'

    # Customize the add/edit forms
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'mobile_number', 'address', 'profile_image_tag', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2', 'mobile_number'),
        }),
    )

    readonly_fields = ('profile_image_tag',)