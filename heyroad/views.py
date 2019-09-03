import json
from itertools import chain
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_duration
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, FormView, \
                                 DeleteView, View
from django.db.models import Sum, Q
from django.middleware.csrf import CsrfViewMiddleware

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from heyroad.permissions import IsOwnerOrReadOnly
from heyroad.models import Route, LatLng, Friendship, Comment
from heyroad.forms import UserRegisterForm, FriendshipInviteForm, CommentForm       
from heyroad.serializers import (
    UserSerializer,
    RouteSerializer,
    UserDetailSerializer,
    RouteDetailSerializer,
    FriendshipSerializer
)
                        

class RouteList(LoginRequiredMixin, ListView):
    # model = Route
    template_name = 'heyroad/route_list.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        friends1 = Friendship.objects                   \
                   .filter(user1=self.request.user)     \
                   .filter(is_accepted=True)            \
                   .values_list('user2', flat=True)
        friends2 = Friendship.objects                   \
                   .filter(user2=self.request.user)     \
                   .filter(is_accepted=True)            \
                   .values_list('user1', flat=True)
        all_friends = list(chain(friends1, friends2))
        all_friends.append(self.request.user)
        queryset = Route.objects.filter(user__in=all_friends)
        return queryset

class UserDetail(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'heyroad/user_routes.html'
    context_object_name = 'user'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

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

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect if requested resource owner is not friend of user
        """
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        if user == self.request.user or Friendship.objects.filter(
            Q(user1=self.request.user, user2=user) |
            Q(user2=self.request.user, user1=user)
           ).filter(is_accepted=True).exists():
           return super(UserDetail, self).dispatch(request, *args, **kwargs)
        return redirect('home')

class RouteDetail(LoginRequiredMixin, DetailView):
    model = Route
    template_name = 'heyroad/route_detail.html'
    context_object_name = 'route'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route = get_object_or_404(Route, pk=self.kwargs.get('pk'))
        # Get route coordinates
        context['latlng_list'] = LatLng.objects.filter(route=route)
        context['comment_list'] = Comment.objects.filter(route=route)
        context['comment_form'] = CommentForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect if requested resource owner is not friend of user
        """
        route = get_object_or_404(Route, pk=self.kwargs.get('pk'))
        user = route.user
        if user == self.request.user or Friendship.objects.filter(
            Q(user1=self.request.user, user2=user) |
            Q(user2=self.request.user, user1=user)
           ).filter(is_accepted=True).exists():
           return super(RouteDetail, self).dispatch(request, *args, **kwargs)
        return redirect('home')

class UserRegister(FormView):
    template_name = 'heyroad/register.html'
    form_class = UserRegisterForm
    success_url = '/login/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class RouteDelete(LoginRequiredMixin, DeleteView):
    model = Route
    template_name = 'heyroad/route_delete.html'
    context_object_name = 'route'
    success_url = "/"

    def get_queryset(self):
        owner = self.request.user
        pk = self.kwargs.get('pk')
        return self.model.objects.filter(pk=pk).filter(user=owner)

class FriendView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        friend_list = Friendship.objects.filter(
            Q(user2=request.user) |  Q(user1=request.user),
            is_accepted=True
        )
        request_list = Friendship.objects.filter(
            user2=request.user,
            is_accepted=False
        )
        invite_form = FriendshipInviteForm()
        return render(request, 'heyroad/friends.html',
                      {'friend_list': friend_list,
                       'request_list': request_list,
                       'invite_form': invite_form})

    def post(self, request):
        error = None
        try:
            # check csrf
            check = CsrfViewMiddleware().process_view(request, None, (), {})
            if check:
                raise PermissionError
            
            # check request action
            if request.POST['action'] == 'invite':
                form = FriendshipInviteForm(request.POST)
                if form.is_valid():
                    user2 = User.objects.get(
                        username=form.cleaned_data['invited_username']
                    )
                    new_friendship = Friendship.objects.create(
                        user1=request.user,
                        user2=user2,
                        is_accepted=False
                    )
                    new_friendship.save()
            elif request.POST['action'] == 'accept':
                friendship_obj = Friendship.objects.get(pk=request.POST['pk'])
                if friendship_obj.user2 == request.user:
                    friendship_obj.is_accepted = True
                    friendship_obj.save()
                else: raise PermissionError
            elif request.POST['action'] == 'decline':
                friendship_obj = Friendship.objects.get(pk=request.POST['pk'])
                if (friendship_obj.user1 == request.user or 
                    friendship_obj.user2 == request.user):
                    friendship_obj.delete()
                else: raise PermissionError
        except Exception as e:
            error = 'Error: ' + str(e)

        friend_list = Friendship.objects.filter(
            Q(user2=request.user) |  Q(user1=request.user),
            is_accepted=True
        )
        request_list = Friendship.objects.filter(
            user2=request.user,
            is_accepted=False
        )
        invite_form = FriendshipInviteForm()
        return render(request, 'heyroad/friends.html',
                      {'friend_list': friend_list,
                       'request_list': request_list,
                       'invite_form': invite_form,
                       'error': error})

class CommentCreateView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def _get_queryset(self, request):
        friends1 = Friendship.objects                   \
                   .filter(user1=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user2', flat=True)
        friends2 = Friendship.objects                   \
                   .filter(user2=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user1', flat=True)
        all_friends = list(chain(friends1, friends2))
        all_friends.append(request.user)
        queryset = Route.objects.filter(user__in=all_friends)
        return queryset

    def get(self, request):
        return redirect('home')

    def post(self, request):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.date = timezone.now()
            queryset = self._get_queryset(request)
            comment.route = get_object_or_404(
                queryset, pk=request.POST['route-pk']
            )
            comment.save()
            return redirect('route', pk=request.POST['route-pk'])

        return redirect('home')
    
class CommentDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        return redirect('home')
    
    def post(self, request):
        try:
            # check csrf
            check = CsrfViewMiddleware().process_view(request, None, (), {})
            if check:
                raise PermissionError
            
            comment = get_object_or_404(Comment, pk=request.POST['pk'])
            if comment.user == request.user:
                route_pk = comment.route.pk
                comment.delete()
                return redirect('route', pk=route_pk)
            else:
                raise PermissionError
        except Exception as e:
            error = 'Error: ' + str(e)
        
        return redirect('home')


# -------------- REST API ----------------

class UserViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def _get_queryset(self, request):
        friends1 = Friendship.objects                   \
                   .filter(user1=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user2', flat=True)
        friends2 = Friendship.objects                   \
                   .filter(user2=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user1', flat=True)
        all_friends = list(chain(friends1, friends2))
        all_friends.append(request.user.pk)
        queryset = User.objects.filter(pk__in=all_friends)
        return queryset

    def list(self, request):
        queryset = self._get_queryset(request)
        serializer = UserSerializer(queryset,
                                    context={'request': request},
                                    many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self._get_queryset(request)
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)

class RouteViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def _get_queryset(self, request):
        friends1 = Friendship.objects                   \
                   .filter(user1=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user2', flat=True)
        friends2 = Friendship.objects                   \
                   .filter(user2=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user1', flat=True)
        all_friends = list(chain(friends1, friends2))
        all_friends.append(request.user)
        queryset = Route.objects.filter(user__in=all_friends)
        return queryset

    def list(self, request):
        queryset = self._get_queryset(request)
        serializer = RouteSerializer(queryset,
                                     context={'request': request},
                                     many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self._get_queryset(request)
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

    def destroy(self, request, pk=None):
        route = Route.objects.get(pk=pk)
        if route.user == request.user:
            route.delete()
            result = {'result': 'success'}
            return Response(result, status=status.HTTP_200_OK)
        result = {'result': 'failed_unauthorized'}
        return Response(result, status=status.HTTP_401_UNAUTHORIZED)

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

class FriendViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def _get_queryset(self, request):
        queryset = Friendship.objects.filter(
            Q(user2=request.user) |  Q(user1=request.user)
        )
        return queryset

    def list(self, request):
        queryset = self._get_queryset(request)
        serializer = FriendshipSerializer(
            queryset, context={'request': request}, many=True
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self._get_queryset(request)
        friendship = get_object_or_404(queryset, pk=pk)
        serializer = FriendshipSerializer(
            friendship, context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # create friendship object
        user2 = get_object_or_404(User, username=body['user2'])
        new_friendship = Friendship.objects.create(
            user1=request.user,
            user2=user2,
            is_accepted=False
        )
        new_friendship.save()

        result = {'result': 'success'}
        return Response(result, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        queryset = Friendship.objects.filter(user2=request.user)
        friendship = get_object_or_404(queryset, pk=pk)
        if body['is_accepted'] == "True":
            friendship.is_accepted = True
            friendship.save()

        result = {'result': 'success'}
        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        queryset = self._get_queryset(request)
        friendship = get_object_or_404(queryset, pk=pk)
        friendship.delete()
        result = {'result': 'success'}
        return Response(result, status=status.HTTP_200_OK)
        
class CommentViewSet(viewsets.ViewSet):
    authentication_classess = [TokenAuthentication]
    permission_classess = [permissions.IsAuthenticated]

    # TODO z jakiegos powodu request bez tokena wchodzi do create
    # i wywala sie na filtrze
    def create(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # get routes
        friends1 = Friendship.objects                   \
                   .filter(user1=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user2', flat=True)
        friends2 = Friendship.objects                   \
                   .filter(user2=request.user)          \
                   .filter(is_accepted=True)            \
                   .values_list('user1', flat=True)
        all_friends = list(chain(friends1, friends2))
        all_friends.append(request.user)
        queryset = Route.objects.filter(user__in=all_friends)

        # create comment object
        route = get_object_or_404(queryset, pk=body['route'])
        new_comment = Comment.objects.create(
            user=request.user,
            route=route,
            date=timezone.now(),
            text=body['text']
        )
        new_comment.save()

        result = {'result': 'success'}
        return Response(result, status=status.HTTP_201_CREATED)
        

    def destroy(self, request, pk=None):
        queryset = Comment.objects.filter(user=request.user)
        comment = get_object_or_404(queryset, pk=pk)
        comment.delete()
        result = {'result': 'success'}
        return Response(result, status=status.HTTP_200_OK)
