from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Route(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    distance = models.FloatField()
    date = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(default=timedelta(minutes=20))

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return "{}_{}_{}".format(self.user,
                                 self.distance,
                                 self.duration)

class LatLng(models.Model):
    route = models.ForeignKey('Route', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()