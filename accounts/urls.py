# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CaretakerViewSet

router = DefaultRouter()
router.register(r"caretakers", CaretakerViewSet, basename="caretaker")

urlpatterns = [
    path("", include(router.urls)),
]
