from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Notification

User = get_user_model()

DEFAULT_PROFILE_PICTURE = 'profile_pics/default.png'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(write_only=True, required=False)
    is_staff = serializers.BooleanField(read_only=True)
    mobile_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name', 'last_name', 'name',
            'is_staff', 'mobile_number', 'address', 'profile_picture'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_mobile_number(self, value):
        # Basic validation: allow digits, +, -, spaces
        if value in (None, ''):
            return value
        import re
        if not re.match(r'^[0-9\+\-\s]{5,30}$', value):
            raise serializers.ValidationError('Invalid mobile number format')
        return value

    def create(self, validated_data):
        # Extract and normalize fields
        name = validated_data.pop('name', '')
        password = validated_data.pop('password')

        # Extract profile fields
        profile_picture = validated_data.pop('profile_picture', None)

        # Ensure username exists (use email as fallback)
        if not validated_data.get('username'):
            validated_data['username'] = validated_data.get('email', '')

        # Set first_name from provided `name`
        if name:
            validated_data['first_name'] = name

        # Use create_user helper which typically handles password hashing
        user = User.objects.create_user(password=password, **validated_data)

        # Assign profile_picture if provided
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()

        return user

    def update(self, instance, validated_data):
        # Handle password separately
        password = validated_data.pop('password', None)
        name = validated_data.pop('name', None)

        profile_picture = validated_data.pop('profile_picture', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if name is not None:
            instance.first_name = name

        if password:
            instance.set_password(password)

        if profile_picture is not None:
            instance.profile_picture = profile_picture

        instance.save()
        return instance

    def to_representation(self, instance):
        """Ensure `profile_picture` always returns a URL. If request is
        present in serializer context, build an absolute URI; otherwise
        return the MEDIA_URL-prefixed path to the default image when missing.
        """
        data = super().to_representation(instance)
        pic = data.get('profile_picture')
        # If serializer returned a falsy profile_picture, provide default URL
        if not pic:
            request = self.context.get('request') if hasattr(self, 'context') else None
            default_path = DEFAULT_PROFILE_PICTURE
            if request:
                data['profile_picture'] = request.build_absolute_uri(settings.MEDIA_URL + default_path)
            else:
                data['profile_picture'] = f"{settings.MEDIA_URL}{default_path}"
        return data


class NotificationSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ('id', 'title', 'body', 'read', 'created_at', 'email', 'related_request', 'summary')
        read_only_fields = ('id', 'created_at')

    def get_summary(self, obj):
        # Prefer a concise summary derived from a related request when present
        try:
            if obj.related_request:
                rq = obj.related_request
                return f"Request #{rq.id} — {rq.customer_name} — {rq.status}"
        except Exception:
            pass
        # Fallback: return a short plain-text excerpt of the body
        if obj.body:
            import re
            # strip HTML tags if present
            text = re.sub('<[^<]+?>', '', obj.body)
            return (text.strip()[:180] + '...') if len(text.strip()) > 180 else text.strip()
        return obj.title or ''