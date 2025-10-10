from rest_framework import serializers
from .models import HealthMetric, MetricReading, PushSubscription, AuditLog


class HealthMetricSerializer(serializers.ModelSerializer):
    readings_count = serializers.SerializerMethodField()
    latest_reading = serializers.SerializerMethodField()

    class Meta:
        model = HealthMetric
        fields = [
            'id', 'name', 'data', 'recorded_at', 
            'readings_count', 'latest_reading'
        ]
        read_only_fields = ['id', 'recorded_at']

    def get_readings_count(self, obj):
        return obj.readings.count()

    def get_latest_reading(self, obj):
        latest = obj.readings.first()
        if latest:
            return MetricReadingSerializer(latest, context=self.context).data
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MetricReadingSerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source='metric.name', read_only=True)

    class Meta:
        model = MetricReading
        fields = [
            'id', 'metric', 'metric_name', 'metric_key', 'recorded_at', 
            'values', 'systolic', 'diastolic', 'glucose_level', 
            'weight', 'heart_rate', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # Ensure metric belongs to the user (if provided)
        request = self.context.get('request')
        if request and 'metric' in data and data['metric']:
            if data['metric'].user != request.user:
                raise serializers.ValidationError("You can only create readings for your own metrics.")
        
        # Validate blood pressure values
        systolic = data.get('systolic')
        diastolic = data.get('diastolic')
        if systolic and diastolic:
            if systolic <= diastolic:
                raise serializers.ValidationError("Systolic pressure must be higher than diastolic pressure.")
            if systolic < 70 or systolic > 300:
                raise serializers.ValidationError("Systolic pressure must be between 70 and 300 mmHg.")
            if diastolic < 40 or diastolic > 200:
                raise serializers.ValidationError("Diastolic pressure must be between 40 and 200 mmHg.")

        # Validate glucose level
        glucose_level = data.get('glucose_level')
        if glucose_level and (glucose_level < 20 or glucose_level > 800):
            raise serializers.ValidationError("Glucose level must be between 20 and 800 mg/dL.")

        # Validate weight
        weight = data.get('weight')
        if weight and (weight < 0.5 or weight > 1000):
            raise serializers.ValidationError("Weight must be between 0.5 and 1000 kg.")

        # Validate heart rate
        heart_rate = data.get('heart_rate')
        if heart_rate and (heart_rate < 20 or heart_rate > 300):
            raise serializers.ValidationError("Heart rate must be between 20 and 300 bpm.")

        return data


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = [
            'id', 'platform', 'endpoint', 'keys', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.full_name', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'actor', 'actor_name', 
            'action', 'object_type', 'object_id', 'before', 
            'after', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MetricReadingCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating readings with common metric types"""
    
    class Meta:
        model = MetricReading
        fields = [
            'metric_key', 'recorded_at', 'values', 
            'systolic', 'diastolic', 'glucose_level', 
            'weight', 'heart_rate', 'notes'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # Try to link to existing metric if available
        metric_key = validated_data.get('metric_key')
        if metric_key:
            try:
                metric = HealthMetric.objects.get(
                    user=validated_data['user'], 
                    name=metric_key
                )
                validated_data['metric'] = metric
            except HealthMetric.DoesNotExist:
                pass
        
        return super().create(validated_data)


class HealthMetricDetailSerializer(HealthMetricSerializer):
    """Extended serializer with recent readings"""
    recent_readings = serializers.SerializerMethodField()
    
    class Meta(HealthMetricSerializer.Meta):
        fields = HealthMetricSerializer.Meta.fields + ['recent_readings']
    
    def get_recent_readings(self, obj):
        recent_readings = obj.readings.all()[:20]  # Last 20 readings
        return MetricReadingSerializer(recent_readings, many=True, context=self.context).data