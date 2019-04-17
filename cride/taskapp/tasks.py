""" Celery tasks. """

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from celery.decorators import task, periodic_task

# Models
from cride.rides.models import Ride
from cride.users.models import User

# Utilities
import jwt
import datetime
import time
from django.utils import timezone


def gen_verification_token(user):
    """ Create JWT Token that the user can use to verify its account. """

    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    payload = {
        'user': user.username,
        'exp': int(expiration.timestamp()),
        'type': 'email_confirmation'
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token.decode()


@task(name='send_confirmation_email', max_entries=3)
def send_confirmation_email(user_pk):
    """ Send account verification link to given user. """

    for i in range(30):
        time.sleep(1)
        print('Sleeping', str(i+1))

    user = User.objects.get(pk=user_pk)
    verification_token = gen_verification_token(user)

    subject = 'Welcome @{}! Verify your account to start using Comparte Ride'.format(user.username)
    from_email = 'Comparte Ride <noreply@comparteride.com>'

    html_content = render_to_string('emails/users/account_verification.html', {
        'user': user,
        'token': verification_token
    })
    msg = EmailMultiAlternatives(subject, html_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@periodic_task(name='disable_finished_rides', run_every=datetime.timedelta(seconds=5))
def disable_finished_rides():
    """ Disabled finished rides. """

    now = timezone.now()
    offset = now + datetime.timedelta(seconds=5)

    # Update rides that have already finished
    rides = Ride.objects.filter(arrival_date__gte=now, arrival_date__lte=offset, is_active=True)
    rides.update(is_active=False)
