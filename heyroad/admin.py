from django.contrib import admin

from .models import Route, LatLng, Friendship, Comment

admin.site.register(Route)
admin.site.register(LatLng)
admin.site.register(Friendship)
admin.site.register(Comment)