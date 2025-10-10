from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'medicines', views.MedicineViewSet, basename='medicine')
router.register(r'medicine-attributes', views.MedicineAttributeViewSet, basename='medicine-attribute')
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')
router.register(r'reminders', views.ReminderViewSet, basename='reminder')
router.register(r'intakes', views.IntakeViewSet, basename='intake')

app_name = 'medicines'

urlpatterns = [
    path('', include(router.urls)),
]