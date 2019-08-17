from django.urls import path
from . import views

urlpatterns = [
    path('', views.RouteList.as_view(), name='home'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user'),
    path('route/<int:pk>/', views.RouteDetail.as_view(), name='route'),
    path('route/<int:pk>/delete/',
         views.RouteDelete.as_view(),
         name='route-delete'),
    path('register/', views.UserRegister.as_view(), name='register'),
]