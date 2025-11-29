from rest_framework import serializers
from django.utils import timezone
from .models import HealthTemplate, HealthRecord


class HealthTemplateSerializer(serializers.ModelSerializer):
    """Serializer for HealthTemplate model (read-only for users)"""
    
    class Meta:
        model = HealthTemplate
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "category",
            "schema",
            "normal_range",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # All fields are read-only for regular users


class HealthTemplateListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing templates"""
    
    class Meta:
        model = HealthTemplate
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "category",
            "is_active",
        ]


class HealthRecordSerializer(serializers.ModelSerializer):
    """Serializer for HealthRecord model with template details"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_slug = serializers.SlugField(source='template.slug', read_only=True)
    template_icon = serializers.CharField(source='template.icon', read_only=True)
    template_schema = serializers.JSONField(source='template.schema', read_only=True)
    template_normal_range = serializers.JSONField(source='template.normal_range', read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            "id",
            "template",
            "template_name",
            "template_slug",
            "template_icon",
            "template_schema",
            "template_normal_range",
            "data",
            "recorded_at",
            "notes",
            "location",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_template(self, value):
        """Ensure template is active"""
        if not value.is_active:
            raise serializers.ValidationError("This template is not available.")
        return value

    def validate(self, attrs):
        """Validate data against template schema"""
        template = attrs.get('template')
        data = attrs.get('data')
        
        if template and data:
            is_valid, errors = template.validate_data(data)
            if not is_valid:
                raise serializers.ValidationError({"data": errors})
        
        return attrs


class HealthRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating health records"""
    
    class Meta:
        model = HealthRecord
        fields = [
            "template",
            "data",
            "recorded_at",
            "notes",
            "location",
        ]

    def validate_template(self, value):
        """Ensure template is active"""
        if not value.is_active:
            raise serializers.ValidationError("This template is not available.")
        return value

    def validate(self, attrs):
        """Validate data against template schema"""
        template = attrs.get('template')
        data = attrs.get('data')
        
        if template and data:
            is_valid, errors = template.validate_data(data)
            if not is_valid:
                raise serializers.ValidationError({"data": errors})
        
        # Default recorded_at to now if not provided
        if not attrs.get('recorded_at'):
            attrs['recorded_at'] = timezone.now()
        
        return attrs

    def create(self, validated_data):
        """Create health record with user from request"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class HealthRecordUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating health records (cannot change template)"""
    
    class Meta:
        model = HealthRecord
        fields = [
            "data",
            "recorded_at",
            "notes",
            "location",
        ]

    def validate(self, attrs):
        """Validate data against template schema if data is being updated"""
        data = attrs.get('data')
        
        if data:
            template = self.instance.template
            is_valid, errors = template.validate_data(data)
            if not is_valid:
                raise serializers.ValidationError({"data": errors})
        
        return attrs


class HealthRecordListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing health records"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_slug = serializers.SlugField(source='template.slug', read_only=True)
    template_icon = serializers.CharField(source='template.icon', read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            "id",
            "template",
            "template_name",
            "template_slug",
            "template_icon",
            "data",
            "recorded_at",
            "notes",
            "location",
            "created_at",
        ]
