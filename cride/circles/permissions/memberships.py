""" Memberships permission classes. """

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership


class IsActiveCircleMember(BasePermission):
    """ Allow access only to circle members.

    Expect that the views implementing
    have a `circle` attribute assigned.
    """

    def has_permission(self, request, view):
        try:
            Membership.objects.get(
                user=request.user,
                circle=view.circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False

        return True
