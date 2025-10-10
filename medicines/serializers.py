from rest_framework import serializers
from django.utils import timezone
from .models import Medicine, MedicineAttribute, Schedule, Reminder, Intake
from .tasks import expand_schedule_rrule


class MedicineAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineAttribute
        fields = [
            'id', 'form', 'composition', 'dose', 'dose_unit', 
            'schedule', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MedicineSerializer(serializers.ModelSerializer):
    attributes = MedicineAttributeSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Medicine
        fields = [
            'id', 'name', 'brand', 'image', 'image_url', 'start_date', 
            'until', 'notes', 'attributes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ScheduleSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'medicine', 'medicine_name', 'timezone', 'time', 'date', 
            'end_date', 'rrule', 'instruction', 'dose_amount', 'dose_unit', 
            'dose', 'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        schedule = super().create(validated_data)
        
        # Trigger reminder generation
        expand_schedule_rrule.delay(schedule.id)
        
        return schedule

    def update(self, instance, validated_data):
        schedule = super().update(instance, validated_data)
        
        # Regenerate reminders if schedule changed
        expand_schedule_rrule.delay(schedule.id)
        
        return schedule

    def validate(self, data):
        # Validate that medicine belongs to the user
        request = self.context.get('request')
        if request and 'medicine' in data:
            medicine = data['medicine']
            if medicine.user != request.user:
                raise serializers.ValidationError("You can only create schedules for your own medicines.")
        
        # Validate date is not in the past (for new schedules)
        if not self.instance and 'date' in data:
            if data['date'] < timezone.now().date():
                raise serializers.ValidationError("Schedule date cannot be in the past.")
        
        return data


class ReminderSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='schedule.medicine.name', read_only=True)
    schedule_time = serializers.TimeField(source='schedule.time', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'schedule', 'medicine_name', 'schedule_time', 'status', 
            'next_run', 'snooze_until', 'triggered_at', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'triggered_at', 'resolved_at']


class ReminderActionSerializer(serializers.Serializer):
    """Serializer for reminder actions like snooze/dismiss"""
    snooze_minutes = serializers.IntegerField(min_value=1, max_value=1440, required=False)  # Max 24 hours
    note = serializers.CharField(max_length=500, required=False)


class IntakeSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = Intake
        fields = [
            'id', 'medicine', 'medicine_name', 'schedule', 'reminder', 'status',
            'scheduled_time', 'taken_at', 'recorded_by', 'recorded_by_name',
            'actual_dose', 'actual_dose_unit', 'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['recorded_by'] = self.context['request'].user
        
        # Set taken_at to now if status is 'taken' and taken_at not provided
        if validated_data.get('status') == 'taken' and not validated_data.get('taken_at'):
            validated_data['taken_at'] = timezone.now()
        
        intake = super().create(validated_data)
        
        # Update related reminder if provided
        if intake.reminder:
            reminder = intake.reminder
            if intake.status == 'taken':
                reminder.status = 'taken'
                reminder.resolved_at = timezone.now()
            elif intake.status == 'missed':
                reminder.status = 'missed'
                reminder.resolved_at = timezone.now()
            reminder.save()
        
        return intake

    def validate(self, data):
        # Validate that medicine belongs to the user
        request = self.context.get('request')
        if request and 'medicine' in data:
            medicine = data['medicine']
            if medicine.user != request.user:
                raise serializers.ValidationError("You can only create intakes for your own medicines.")
        
        # Validate that schedule belongs to the medicine (if provided)
        if 'schedule' in data and 'medicine' in data:
            if data['schedule'] and data['schedule'].medicine != data['medicine']:
                raise serializers.ValidationError("Schedule must belong to the specified medicine.")
        
        # Validate that reminder belongs to the schedule (if provided)
        if 'reminder' in data and 'schedule' in data:
            if data['reminder'] and data['reminder'].schedule != data['schedule']:
                raise serializers.ValidationError("Reminder must belong to the specified schedule.")
        
        return data


class MedicineDetailSerializer(MedicineSerializer):
    """Extended serializer with schedules and recent intakes"""
    schedules = ScheduleSerializer(many=True, read_only=True)
    recent_intakes = serializers.SerializerMethodField()
    
    class Meta(MedicineSerializer.Meta):
        fields = MedicineSerializer.Meta.fields + ['schedules', 'recent_intakes']
    
    def get_recent_intakes(self, obj):
        recent_intakes = obj.intakes.all()[:10]  # Last 10 intakes
        return IntakeSerializer(recent_intakes, many=True, context=self.context).data