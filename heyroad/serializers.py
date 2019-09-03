from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Route, LatLng, Friendship, Comment


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserDetailSerializer(serializers.ModelSerializer):
    routes = serializers.HyperlinkedRelatedField(many=True,
                                                 view_name='route-detail',
                                                 read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'routes']

class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ['id', 'user', 'distance', 'date', 'duration']

class LatLngSerializer(serializers.ModelSerializer):

    class Meta:
        model = LatLng
        fields = ['latitude', 'longitude']

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'user', 'route', 'date', 'text']

class RouteDetailSerializer(serializers.ModelSerializer):
    coords = LatLngSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'user', 'distance', 'date', 'duration', 'coords',
                  'comments']

class FriendshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friendship
        fields = ['id', 'user1', 'user2', 'is_accepted']
