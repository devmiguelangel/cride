""" Circle serializers. """

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Circle


class CircleModelSerializer(serializers.ModelSerializer):
    """ Circle models serializer. """

    class Meta:
        """ Meta class. """

        model = Circle
        fields = (
            'id', 'name', 'slug_name',
            'about', 'picture',
            'rides_offered', 'rides_taken',
            'is_verified', 'is_public',
            'is_limited', 'members_limit',
        )