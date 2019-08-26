from django.contrib import admin

from .models import Route, LatLng, Friendship

admin.site.register(Route)
admin.site.register(LatLng)
admin.site.register(Friendship)