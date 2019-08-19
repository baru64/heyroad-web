from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')
router.register(r'route', views.RouteViewSet, basename='route')

urlpatterns = [
    path('', views.RouteList.as_view(), name='home'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user'),
    path('route/<int:pk>/', views.RouteDetail.as_view(), name='route'),
    path('route/<int:pk>/delete/',
         views.RouteDelete.as_view(),
         name='route-delete'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]