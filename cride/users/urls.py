""" User URLs. """

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework import routers

# Views
from cride.users.views import users as user_views

router = routers.DefaultRouter()
router.register(r'users', user_views.UserViewSet, base_name='users')

urlpatterns = [
    path('', include(router.urls)),
]
