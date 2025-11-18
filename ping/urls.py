from django.urls import path
from . import views

urlpatterns = [
    path("", views.small_ping, name="Minimal ping"),

    path("home/", views.ping, name="test connection"),
    path("test/", views.ping, name="test connection"),
]
