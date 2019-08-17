from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, FormView, \
                                 DeleteView
from django.db.models import Sum

from heyroad.models import Route, LatLng
from heyroad.forms import UserRegisterForm #, RouteDeleteForm

# TODO class-based views
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

# TODO:
# API CREATE/DELETE/GET ROUTE, REGISTER/LOGIN USER