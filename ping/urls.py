from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.ping, name='test connection'),
    path('test/', views.ping, name='test connection'),
]