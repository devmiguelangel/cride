""" Circles URLs """

# Django
from django.urls import path, include

# Django REST Framework
from rest_framework import routers

# Views
from cride.circles.views import circles as circle_views
from cride.circles.views import memberships as membership_views

router = routers.DefaultRouter()
router.register(r'circles', circle_views.CircleViewSet, base_name='circles')
router.register(r'circles/(?P<slug_name>[-a-zA-Z0-9_]+)/members',
                membership_views.MembershipViewSet,
                base_name='membership')

urlpatterns = [
    path('', include(router.urls)),
]
