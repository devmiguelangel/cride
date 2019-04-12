""" Profile model. """

# Django
from django.db import models
# Models
from cride.utils.models import CRideModel
from .users import User


class Profile(CRideModel):
    """ Profile model.

    A profile holds a user's public data like biography, picture,
    and statistics.
    """

    user = models.OneToOneField(User, models.CASCADE)

    picture = models.ImageField(
        'profile picture',
        upload_to='users/pictures/',
        blank=True,
        null=True
    )
    biography = models.TextField(max_length=500, blank=True)

    # Stats
    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)
    reputation = models.FloatField(
        default=5.0,
        help_text='Users reputation based on the rides taken and offered'
    )

    def __str__(self):
        """ Return user's str representation. """
        return str(self.user)