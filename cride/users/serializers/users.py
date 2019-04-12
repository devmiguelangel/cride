""" User serializers. """

# Django
from django.contrib.auth import authenticate

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Models
from cride.users.models import User


class UserModelSerializer(serializers.ModelSerializer):
    """ User model serializer. """

    class Meta:
        """ Meta class. """

        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')


class UserLoginSerializer(serializers.Serializer):
    """ User login serializer.

    Handle the login request data.
    """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, max_length=64)

    def validate(self, data):
        """ Check credentials. """

        user = authenticate(username=data['email'], password=data['password'])

        if user is not None:
            self.context['user'] = user
            return data

        raise serializers.ValidationError('Invalid credentials')

    def create(self, data):
        """ Generate or retrieve new token. """

        token, created = Token.objects.get_or_create(user=self.context['user'])

        return self.context['user'], token.key
