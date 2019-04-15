""" Circle views. """

# Django REST Framework
from rest_framework import mixins, viewsets

# Permission
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsCircleAdmin

# Serializers
from cride.circles.serializers import CircleModelSerializer

# Models
from cride.circles.models import Circle, Membership


class CircleViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """ Circle view set. """

    # queryset = Circle.objects.all()
    serializer_class = CircleModelSerializer
    # permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """ Restrict list to public only. """

        queryset = Circle.objects.all()

        if self.action == 'list':
            return queryset.filter(is_public=True)

        return queryset

    def get_permissions(self):
        """ Assign permissions based on action. """

        permission_classes = [IsAuthenticated]

        if self.action in ['update', 'partial_update']:
            permission_classes.append(IsCircleAdmin)

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """ Assign circle admin. """

        circle = serializer.save()
        user = self.request.user
        profile = user.profile

        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10
        )

        return super().perform_create(serializer)
