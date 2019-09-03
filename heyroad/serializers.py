from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Route, LatLng, Friendship, Comment


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'username', 'email']

class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    routes = serializers.HyperlinkedRelatedField(many=True,
                                                 view_name='route-detail',
                                                 read_only=True)

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'routes']

class RouteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Route
        fields = ['url', 'user', 'distance', 'date', 'duration']

class LatLngSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = LatLng
        fields = ['latitude', 'longitude']

class CommentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Comment
        fields = ['pk', 'user', 'route', 'date', 'text']

class RouteDetailSerializer(serializers.HyperlinkedModelSerializer):
    coords = LatLngSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['url', 'user', 'distance', 'date', 'duration', 'coords',
                  'comments']

class FriendshipSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Friendship
        fields = ['pk', 'user1', 'user2', 'is_accepted']
