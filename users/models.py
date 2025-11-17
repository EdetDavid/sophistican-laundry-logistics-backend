from django.contrib.auth.models import AbstractUser
from django.db import models


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