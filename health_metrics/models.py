from django.db import models
from django.conf import settings


class HealthMetric(models.Model):
    """User metrics like blood_pressure, blood_sugar stored as JSON"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='health_metrics')
    name = models.CharField(max_length=100, help_text="Metric name like 'Blood Pressure', 'Blood Sugar'")
    data = models.JSONField(default=dict, help_text="Flexible JSON for metric configuration")
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['user', 'name']),
        ]
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.full_name} - {self.name}"


class MetricReading(models.Model):
    """Timestamped readings linked to HealthMetric"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='metric_readings')
    metric = models.ForeignKey(HealthMetric, on_delete=models.CASCADE, blank=True, null=True, related_name='readings')
    metric_key = models.CharField(max_length=100, help_text="Metric identifier for grouping")
    recorded_at = models.DateTimeField()
    values = models.JSONField(help_text="JSON object containing the metric values")
    
    # Optional fields for common scenarios
    systolic = models.IntegerField(blank=True, null=True, help_text="For Blood Pressure")
    diastolic = models.IntegerField(blank=True, null=True, help_text="For Blood Pressure")
    glucose_level = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="For Blood Sugar")
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="For Weight")
    heart_rate = models.IntegerField(blank=True, null=True, help_text="For Heart Rate")
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['user', 'metric_key']),
            models.Index(fields=['user', 'metric_key', '-recorded_at']),
            models.Index(fields=['metric']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.metric_key} at {self.recorded_at}"


class PushSubscription(models.Model):
    """Store push endpoints for FCM/APNs/web"""
    
    PLATFORM_CHOICES = [
        ('android', 'Android (FCM)'),
        ('ios', 'iOS (APNs)'),
        ('web', 'Web Push'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    endpoint = models.URLField()
    keys = models.JSONField(default=dict, help_text="Push subscription keys and tokens")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['user', 'is_active']),
        ]
        unique_together = ('user', 'endpoint')

    def __str__(self):
        return f"{self.user.full_name} - {self.platform}"


class AuditLog(models.Model):
    """Versioned changes for critical actions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audit_logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performed_actions')
    action = models.CharField(max_length=50, help_text="Action performed like 'create', 'update', 'delete'")
    object_type = models.CharField(max_length=50, help_text="Model name that was affected")
    object_id = models.IntegerField(help_text="ID of the affected object")
    before = models.JSONField(blank=True, null=True, help_text="Object state before change")
    after = models.JSONField(blank=True, null=True, help_text="Object state after change")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['actor']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.actor.full_name} {self.action} {self.object_type}#{self.object_id}"
