""" Circles admin. """

# Django
from django.contrib import admin
from django.http import HttpResponse

# Models
from .models import Circle
from cride.rides.models import Ride

# Utils
import csv
import datetime
from django.utils import timezone


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """ Circle admin. """

    list_display = (
        'slug_name',
        'name',
        'is_public',
        'is_verified',
        'is_limited',
        'members_limit',
    )
    search_fields = ('slug_name', 'name')
    list_filter = ('is_public', 'is_verified', 'is_limited')

    actions = ['make_verified', 'make_unverified', 'download_todays_rides']

    def make_verified(self, request, queryset):
        """ Make circles verified. """

        queryset.update(is_verified=True)

    make_verified.short_description = 'Make selected circles verified.'

    def make_unverified(self, request, queryset):
        """ Make circles unverified. """

        queryset.update(is_verified=False)

    make_unverified.short_description = 'Make selected circles unverified.'

    def download_todays_rides(self, request, queryset):
        """ Return today's rides. """

        now = timezone.now()
        start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        end = start + datetime.timedelta(days=1)
        rides = Ride.objects.filter(offered_in__in=queryset.values_list('id'),
                                    departure_date__gte=start,
                                    departure_date__lte=end).order_by('departure_location')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="rides.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'id',
            'passengers',
            'departure_location',
            'departure_date',
            'arrival_location',
            'arrival_date',
            'rating'
        ])

        for ride in rides:
            writer.writerow([
                ride.pk,
                ride.passengers.count(),
                ride.departure_location,
                str(ride.departure_date),
                ride.arrival_location,
                str(ride.arrival_date),
                ride.rating
            ])

        return response

    download_todays_rides.short_description = 'Download todays rides'
