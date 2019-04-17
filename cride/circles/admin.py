""" Circles admin. """

# Django
from django.contrib import admin

# Models
from .models import Circle


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

    actions = ['make_verified', 'make_unverified']

    def make_verified(self, request, queryset):
        """ Make circles verified. """

        queryset.update(is_verified=True)

    make_verified.short_description = 'Make selected circles verified.'

    def make_unverified(self, request, queryset):
        """ Make circles unverified. """

        queryset.update(is_verified=False)

    make_unverified.short_description = 'Make selected circles unverified.'
