""" Rides URLs """

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework import routers

# Views
from cride.rides.views import rides as ride_views

router = routers.DefaultRouter()
router.register(r'circles/(?P<slug_name>[-a-zA-Z0-9_]+)/rides',
                ride_views.RideViewSet,
                base_name='ride')

urlpatterns = [
    path('', include(router.urls)),
]
