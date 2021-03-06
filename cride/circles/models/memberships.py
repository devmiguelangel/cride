""" Membership model. """

# Django
from django.db import models

# Models
from cride.circles.models import Circle
from cride.users.models import User, Profile

# Utilities
from cride.utils.models import CRideModel


class Membership(CRideModel):
    """ Membership model.

    A membership is the table that holds the relationship between
    a user and a circle.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)

    is_admin = models.BooleanField(
        'circle admin',
        default=False,
        help_text="Circle admins can update the circle's data and manage its members."
    )

    # Invitations
    user_invitations = models.PositiveSmallIntegerField(default=0)
    remaining_invitations = models.PositiveSmallIntegerField(default=0)
    invited_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='invited_by'
    )

    # Stats
    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)

    # Status
    is_active = models.BooleanField(
        'active status',
        default=True,
        help_text='Only active users are allowed to interact in the circle.'
    )

    def __str__(self):
        """ Return username and circle. """

        return '@{username} at #{circle}'.format(user=self.user.username, circle=self.circle.slug_name)
    
