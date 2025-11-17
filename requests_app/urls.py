from django.urls import path, include
from rest_framework import routers
from .views import LaundryRequestViewSet, DriverViewSet

router = routers.DefaultRouter()
router.register(r'requests', LaundryRequestViewSet, basename='laundryrequest')
router.register(r'drivers', DriverViewSet, basename='driver')

urlpatterns = [
    path('', include(router.urls)),
]
