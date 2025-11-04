from django.urls import path
from . import views

urlpatterns = [
    path("", views.medicines, name="medicines"),
    path("<int:medicine_id>/", views.medicine_detail, name="medicine_detail"),
]
