from django.contrib import admin
from .models import HealthMetric, MetricReading, PushSubscription, AuditLog


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'recorded_at')
    list_filter = ('name', 'recorded_at')
    search_fields = ('name', 'user__full_name', 'user__email')
    ordering = ('-recorded_at',)


@admin.register(MetricReading)
class MetricReadingAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'metric_key', 'recorded_at', 'systolic', 'diastolic', 
        'glucose_level', 'weight', 'heart_rate'
    )
    list_filter = ('metric_key', 'recorded_at', 'created_at')
    search_fields = ('user__full_name', 'metric_key', 'notes')
    ordering = ('-recorded_at',)
    readonly_fields = ('created_at',)


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'is_active', 'created_at')
    list_filter = ('platform', 'is_active', 'created_at')
    search_fields = ('user__full_name', 'user__email', 'endpoint')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'action', 'object_type', 'object_id', 'created_at')
    list_filter = ('action', 'object_type', 'created_at')
    search_fields = ('user__full_name', 'actor__full_name', 'action', 'object_type')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
