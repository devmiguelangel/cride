""" Ride views. """

# Django REST Framework.
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Serializers
from cride.rides.serializers import CreateRideSerializer, RideModelSerializer, JoinRideSerializer, EndRideSerializer

# Models
from cride.circles.models import Circle

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsActiveCircleMember
from cride.rides.permissions import IsRideOwner, IsNotRideOwner

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter

# Utilities
import datetime
from django.utils import timezone


class RideViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """ Ride view set. """

    serializer_class = CreateRideSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('departure_location', 'arrival_location')
    ordering_fields = ('departure_date', 'arrival_date', 'available_seats')
    ordering = ('departure_date', 'arrival_date', 'available_seats')

    def dispatch(self, request, *args, **kwargs):
        """ Verify that the circle exists. """

        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(RideViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """ Assign permission based on action. """

        permission_classes = [IsAuthenticated, IsActiveCircleMember]

        if self.action in ['update', 'partial_update', 'finish']:
            permission_classes.append(IsRideOwner)
        if self.action == 'join':
            permission_classes.append(IsNotRideOwner)

        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        """ Add circle to serializer context. """

        context = super(RideViewSet, self).get_serializer_context()
        context['circle'] = self.circle

        return context

    def get_serializer_class(self):
        """ Return serializer based on action. """

        if self.action == 'create':
            return CreateRideSerializer
        if self.action == 'join':
            return JoinRideSerializer
        if self.action == 'finish':
            return EndRideSerializer

        return RideModelSerializer

    def get_queryset(self):
        """ Return active circle's rides. """

        if self.action != 'finish':
            offset = timezone.now() + datetime.timedelta(minutes=10)

            return self.circle.ride_set.filter(departure_date__gte=offset, is_active=True, available_seats__gte=1)

        return self.circle.ride_set.all()

    @action(detail=True, methods=['post'])
    def join(self, request, *args, **kwargs):
        """ Add requesting user to ride. """

        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={'passenger': request.user.pk},
            context={'ride': ride, 'circle': self.circle},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = RideModelSerializer(ride).data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finish(self, request, *args, **kwargs):
        """ Call by owners to finish a ride. """

        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={
                'is_active': False,
                'current_time': timezone.now()
            },
            context=self.get_serializer_context(),
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = RideModelSerializer(ride).data

        return Response(data, status=status.HTTP_200_OK)
