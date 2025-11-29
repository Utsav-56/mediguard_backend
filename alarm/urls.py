from django.urls import path
from .views import AlarmListView, AlarmDetailView

urlpatterns = [
    path('list/', AlarmListView.as_view(), name='alarm-list'),
    path('<int:pk>/', AlarmDetailView.as_view(), name='alarm-detail'),
]