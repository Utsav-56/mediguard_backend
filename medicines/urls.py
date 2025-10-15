from django.urls import include
from django.urls import path
from . import views

urlpatterns = [
    path('medicine/', views.medicines, name='medicines'),
    path('medicine/<int:medicine_id>/', views.medicine_detail, name='medicine_detail'),
]

