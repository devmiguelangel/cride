""" Ride serializers. """

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Membership
from cride.rides.models import Ride

# Serializers
from cride.users.serializers import UserModelSerializer

# Utilities
import datetime
from django.utils import timezone


class CreateRideSerializer(serializers.ModelSerializer):
    """ Create ride serializer. """

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1, max_value=15)

    class Meta:
        """ Meta class. """

        model = Ride
        exclude = ('offered_in', 'passengers', 'rating', 'is_active')

    def validate_departure_date(self, data):
        """ Verify date is not in the past. """

        min_date = timezone.now() + datetime.timedelta(minutes=10)

        if data < min_date:
            raise serializers.ValidationError(
                'Departure time must be at least pas the next 20 minutes window.'
            )

        return data

    def validate(self, data):
        """ Validate.

        Verify that the person who offers the ride is member
        and also the same user making the request.
        """

        if self.context['request'].user != data['offered_by']:
            raise serializers.ValidationError('Rides offered on behalf of others are not allowed.')

        user = data['offered_by']
        circle = self.context['circle']

        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
        except Membership.DoesNotExists:
            raise serializers.ValidationError('User is not an active member of the circle.')

        if data['arrival_date'] <= data['departure_date']:
            raise serializers.ValidationError('Departure date must happen after arrival date.')

        self.context['membership'] = membership
        return data

    def create(self, data):
        """ Create ride and update stats. """

        circle = self.context['circle']
        ride = Ride.objects.create(**data, offered_in=circle)

        # Circle
        circle.rides_offered += 1
        circle.save()

        # Membership
        membership = self.context['membership']
        membership.rides_offered += 1
        membership.save()

        # Profile
        profile = data['offered_by'].profile
        profile.rides_offered += 1
        profile.save()

        return data


class RideModelSerializer(serializers.ModelSerializer):
    """ Ride model serializer. """

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField()

    passengers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        """ Meta class. """

        model = Ride
        fields = '__all__'
        read_only_fields = (
            'offered_by',
            'offered_in',
            'rating',
        )

    def update(self, instance, validated_data):
        """ Allow updates only before departure date. """

        now = timezone.now()

        if instance.departure_date <= now:
            raise serializers.ValidationError('Ongoing rides cannot be modified.')

        return super(RideModelSerializer, self).update(instance, validated_data)
