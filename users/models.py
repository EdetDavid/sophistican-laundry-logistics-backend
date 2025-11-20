from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def profile_picture_upload_to(instance, filename):
    # store uploads under MEDIA_ROOT/profile_pics/<user_id>/<filename>
    return f'profile_pics/{instance.id}/{filename}'


class User(AbstractUser):
    """Custom user model extended with profile fields."""
    mobile_number = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    # Use a default image path under MEDIA_ROOT/profile_pics/default.png so
    # admin and APIs can always return a fallback image if the user hasn't
    # uploaded one. Ensure a real file exists at that path in MEDIA_ROOT.
    profile_picture = models.ImageField(
        upload_to=profile_picture_upload_to, blank=True, null=True,
        default='profile_pics/default.png'
    )


class Notification(models.Model):
    """Simple notification record created when the system sends emails.

    Notifications may be linked to a `User` if the recipient has an account
    in the system; otherwise `user` is null and `email` stores the recipient.
    """
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    email = models.CharField(max_length=254, blank=True, null=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    related_request = models.ForeignKey(
        'requests_app.LaundryRequest', null=True, blank=True, on_delete=models.SET_NULL, related_name='notifications'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification({self.title}) to {self.email or (self.user and self.user.email)}"