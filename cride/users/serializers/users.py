""" User serializers. """

# Django
from django.conf import settings
from django.contrib.auth import authenticate, password_validation
from django.core.mail import EmailMultiAlternatives
from django.core.validators import RegexValidator
from django.template.loader import render_to_string

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from cride.users.models import User, Profile

# Utilities
import jwt
import datetime


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
            if not user.is_verified:
                raise serializers.ValidationError('Account is not active yet :(')

            self.context['user'] = user
            return data

        raise serializers.ValidationError('Invalid credentials')

    def create(self, data):
        """ Generate or retrieve new token. """

        token, created = Token.objects.get_or_create(user=self.context['user'])

        return self.context['user'], token.key


class UserSignUpSerializer(serializers.Serializer):
    """ User sign up serializer.

    Handle sign up data validation and user/profile creation.
    """

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # Phone number
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: +999999999. Up to 15 digits allowed."
    )
    phone_number = serializers.CharField(validators=[phone_regex])

    # Password
    password = serializers.CharField(
        min_length=6,
        max_length=64,
    )
    password_confirmation = serializers.CharField(
        min_length=6,
        max_length=64,
    )

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    def validate(self, data):
        """ Verify password match. """

        password = data['password']
        password_confirmation = data['password_confirmation']

        if password != password_confirmation:
            raise serializers.ValidationError('Passwords dont match.')

        password_validation.validate_password(password=password)

        return data

    def create(self, data):
        """ Handle user and profile creation. """

        data.pop('password_confirmation')
        user = User.objects.create_user(**data, is_verified=False, is_client=True)
        profile = Profile.objects.create(user=user)

        self.send_confirmation_email(user)

        return user

    def send_confirmation_email(self, user):
        """ Send account verification link to given user. """

        verification_token = self.gen_verification_token(user)

        subject = 'Welcome @{}! Verify your account to start using Comparte Ride'.format(user.username)
        from_email = 'Comparte Ride <noreply@comparteride.com>'

        html_content = render_to_string('emails/users/account_verification.html', {
            'user': user,
            'token': verification_token
        })
        msg = EmailMultiAlternatives(subject, html_content, from_email, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def gen_verification_token(self, user):
        """ Create JWT Token that the user can use to verify its account. """

        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        payload = {
            'user': user.username,
            'exp': int(expiration.timestamp()),
            'type': 'email_confirmation'
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return token.decode()


class AccountVerificationSerializer(serializers.Serializer):
    """ Account verification serializer. """

    token = serializers.CharField()

    def validate_token(self, data):
        """ Verify token is valid """

        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired.')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token.')

        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token.')

        self.context['payload'] = payload

        return data

    def save(self, **kwargs):
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        user.is_verified = True
        user.save()
