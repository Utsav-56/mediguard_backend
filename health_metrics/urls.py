from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'health-metrics', views.HealthMetricViewSet, basename='health-metric')
router.register(r'metric-readings', views.MetricReadingViewSet, basename='metric-reading')
router.register(r'push-subscriptions', views.PushSubscriptionViewSet, basename='push-subscription')
router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-log')

app_name = 'health_metrics'

urlpatterns = [
    path('', include(router.urls)),
]