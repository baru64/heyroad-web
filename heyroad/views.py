import json
from django.utils.dateparse import parse_datetime, parse_duration
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, FormView, \
                                 DeleteView
from django.db.models import Sum
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from heyroad.permissions import IsOwnerOrReadOnly
from heyroad.models import Route, LatLng
from heyroad.forms import UserRegisterForm
from heyroad.serializers import UserSerializer, RouteSerializer,        \
                         UserDetailSerializer, RouteDetailSerializer    \

class RouteList(ListView):
    model = Route
    template_name = 'heyroad/route_list.html'

class UserDetail(DetailView):
    model = User
    template_name = 'heyroad/user_routes.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        # Get user routes
        user_routes = Route.objects.filter(user=user)
        context['route_list'] = user_routes
        # Get user stats
        context['user_stats'] = user_routes.aggregate(
                                total_duration=Sum('duration'),
                                total_distance=Sum('distance'))
        return context

class RouteDetail(DetailView):
    model = Route
    template_name = 'heyroad/route_detail.html'
    context_object_name = 'route'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route = get_object_or_404(Route, pk=self.kwargs.get('pk'))
        # Get route coordinates
        context['latlng_list'] = LatLng.objects.filter(route=route)
        return context

class UserRegister(FormView):
    template_name = 'heyroad/register.html'
    form_class = UserRegisterForm
    success_url = '/login/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

# class RouteDelete(LoginRequiredMixin, View): CSRF vulnerable!

#     def post(self, request, pk):
#         route = get_object_or_404(Route, pk=pk)
#         latlng_list = LatLng.objects.filter(route=route)

# class RouteDelete(LoginRequiredMixin, FormView):
#     template_name = 'heyroad/route_delete.html'
#     form_class = RouteDeleteForm
#     success_url = '/'

#     def form_valid(self, form):
#         # delete stuff
#         return super().form_valid()

class RouteDelete(LoginRequiredMixin, DeleteView):
    model = Route
    template_name = 'heyroad/route_delete.html'
    context_object_name = 'route'
    success_url = "/"

    def get_queryset(self):
        owner = self.request.user
        pk = self.kwargs.get('pk')
        return self.model.objects.filter(pk=pk).filter(user=owner)

class UserViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset,
                                    context={'request': request},
                                    many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)

class RouteViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    def list(self, request):
        queryset = Route.objects.all()
        serializer = RouteSerializer(queryset,
                                     context={'request': request},
                                     many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Route.objects.all()
        route = get_object_or_404(queryset, pk=pk)
        serializer = RouteDetailSerializer(route, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        
        # create route object
        distance = float(body['distance'])
        date = parse_datetime(body['date'])
        duration = parse_duration(body['duration'])
        new_route = Route.objects.create(user=request.user,
                                         distance=distance,
                                         duration=duration,
                                         date=date)
        new_route.save()
        # create latlngs
        for coordinate in body['coords']:
            latlng = LatLng.objects.create(route=new_route,
                                           latitude=coordinate['latitude'],
                                           longitude=coordinate['longitude'])
            latlng.save()

        result = {'result': 'success'}
        return Response(result, status=status.HTTP_201_CREATED)

class RegisterAPIView(APIView):

    def post(self, request, format=None):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['username']
        password = body['password']
        email = body['email']

        if User.objects.filter(username=username).exists():
            result = {'result': 'failed_username_used'}
            return Response(result, status=status.HTTP_409_CONFLICT)
        elif User.objects.filter(email=email).exists():
            result = {'result': 'failed_email_used'}
            return Response(result, status=status.HTTP_409_CONFLICT)
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            result = {'result': 'success'}
            return Response(result, status=status.HTTP_201_CREATED)

# TODO:
# - friends
# - route comments
