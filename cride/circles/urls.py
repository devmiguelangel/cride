""" Circles URLs """

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework import routers

# Views
from cride.circles.views import CircleViewSet

router = routers.DefaultRouter()
router.register(r'circles', CircleViewSet, base_name='user')

urlpatterns = [
    path('', include(router.urls)),
]
