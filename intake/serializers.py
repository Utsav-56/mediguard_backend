from rest_framework import serializers
from django.utils import timezone
from .models import Intake
from medicines.models import Medicines


class IntakeSerializer(serializers.ModelSerializer):
    """Serializer for Intake model with computed fields"""
    
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_dosage = serializers.IntegerField(source='medicine.dosage', read_only=True)
    medicine_amount = serializers.IntegerField(source='medicine.amount', read_only=True)
    is_late = serializers.BooleanField(read_only=True)
    delay_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Intake
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_dosage",
            "medicine_amount",
            "scheduled_date",
            "scheduled_time",
            "status",
            "taken_at",
            "notes",
            "is_late",
            "delay_minutes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at", "is_late", "delay_minutes"]

    def validate_medicine(self, value):
        """Ensure the medicine belongs to the requesting user"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("You can only create intakes for your own medicines.")
        return value

    def validate(self, attrs):
        """Custom validation for intake data"""
        status = attrs.get('status')
        taken_at = attrs.get('taken_at')

        # If status is 'taken', taken_at should be provided
        if status == 'taken' and not taken_at:
            # Auto-set taken_at to current time if not provided
            attrs['taken_at'] = timezone.now()

        # If status is not 'taken', clear taken_at
        if status in ['pending', 'skipped', 'missed']:
            attrs['taken_at'] = None

        return attrs


class IntakeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new intake records"""

    class Meta:
        model = Intake
        fields = [
            "medicine",
            "scheduled_date",
            "scheduled_time",
            "status",
            "taken_at",
            "notes",
        ]

    def validate_medicine(self, value):
        """Ensure the medicine belongs to the requesting user"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("You can only create intakes for your own medicines.")
        return value

    def create(self, validated_data):
        """Create intake with user from request"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class IntakeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating intake records (mainly status)"""

    class Meta:
        model = Intake
        fields = [
            "status",
            "taken_at",
            "notes",
        ]

    def validate(self, attrs):
        """Auto-set taken_at when marking as taken"""
        status = attrs.get('status')
        taken_at = attrs.get('taken_at')

        if status == 'taken' and not taken_at:
            attrs['taken_at'] = timezone.now()

        if status in ['pending', 'skipped', 'missed']:
            attrs['taken_at'] = None

        return attrs


class IntakeBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating intake records for a date range"""
    
    start_date = serializers.DateField(help_text="Start date for generating intakes")
    end_date = serializers.DateField(help_text="End date for generating intakes")
    medicine_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of medicine IDs. If empty, generates for all user medicines."
    )

    def validate(self, attrs):
        """Validate date range"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date > end_date:
            raise serializers.ValidationError("start_date must be before or equal to end_date")

        # Limit to 30 days to prevent abuse
        delta = (end_date - start_date).days
        if delta > 30:
            raise serializers.ValidationError("Date range cannot exceed 30 days")

        return attrs


class IntakeStatsSerializer(serializers.Serializer):
    """Serializer for intake statistics"""
    
    total_intakes = serializers.IntegerField()
    taken_count = serializers.IntegerField()
    missed_count = serializers.IntegerField()
    skipped_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    adherence_rate = serializers.FloatField(help_text="Percentage of taken intakes out of total non-pending")
    on_time_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
