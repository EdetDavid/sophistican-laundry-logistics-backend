from rest_framework import viewsets, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from utils.email_service import notify_new_user_registration, notify_user_signup_confirmation
from rest_framework import mixins
from .serializers import NotificationSerializer
from django.shortcuts import get_object_or_404
from .models import Notification
from django.db import models

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    # Use token authentication for user endpoints to avoid CSRF issues
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Allow anyone to register
            return [permissions.AllowAny()]
        elif self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            # Only staff can list all users and modify other users
            return [permissions.IsAdminUser()]
        # Other actions (like 'me') require just authentication
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Staff users can see all users
        if self.request.user.is_staff:
            return self.request.user.__class__.objects.all()
        # Regular users can only see themselves
        return self.request.user.__class__.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    # Avoid SessionAuthentication for these endpoints so CSRF is not enforced
    # TokenAuthentication does not require CSRF for unsafe methods and
    # allows unauthenticated requests to the login/signup actions.
    authentication_classes = [TokenAuthentication]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'detail': 'Please provide both email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            # create or retrieve token for the user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'detail': 'Successfully logged in'
            })
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=['post'])
    def signup(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')
        mobile_number = request.data.get('mobile_number')
        address = request.data.get('address')
        profile_picture = request.FILES.get('profile_picture') if hasattr(request, 'FILES') else None

        if not email or not password or not name:
            return Response(
                {'detail': 'Please provide email, password and name'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if User.objects.filter(username=email).exists():
            return Response(
                {'detail': 'User already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            mobile_number=mobile_number or None,
            address=address or None,
        )
        # attach profile picture if uploaded
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        
        # create token and login
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        
        # Send email notifications
        notify_new_user_registration(user)  # Notify admins
        notify_user_signup_confirmation(user)  # Notify the new user
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'detail': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out'})


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """List and manage notifications belonging to the authenticated user.

    - GET /notifications/ : list notifications for the current user (or email)
    - POST /notifications/{id}/mark_read/ : mark a notification as read
    - DELETE /notifications/{id}/ : delete a notification
    - POST /notifications/clear_all/ : clear (delete) all notifications for user
    """
    serializer_class = NotificationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Notifications linked to the user OR matching the user's email
        qs = Notification.objects.filter(models.Q(user=user) | models.Q(email__iexact=user.email))
        return qs

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        obj = get_object_or_404(self.get_queryset(), pk=pk)
        obj.read = True
        obj.save()
        return Response({'detail': 'marked read'})

    @action(detail=False, methods=['post'])
    def clear_all(self, request):
        user = request.user
        Notification.objects.filter(models.Q(user=user) | models.Q(email__iexact=user.email)).delete()
        return Response({'detail': 'cleared'})