from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


def medicine_image_path(instance, filename):
    """File will be uploaded to MEDIA_ROOT/medicine_images/user_<id>/<filename>"""
    ext = filename.split(".")[-1]
    return f"medicine_images/user_{instance.user.id}/{filename}"


class Medicine(models.Model):
    """User-specific medicine record"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=medicine_image_path, blank=True, null=True)
    start_date = models.DateField()
    until = models.DateField(blank=True, null=True)  # End date for medicine course
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['user', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.full_name})"


class MedicineAttribute(models.Model):
    """Details about medicine - flexible JSON for composition"""
    
    FORM_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('drops', 'Drops'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('powder', 'Powder'),
        ('inhaler', 'Inhaler'),
        ('patch', 'Patch'),
        ('other', 'Other'),
    ]

    DOSE_UNIT_CHOICES = [
        ('mg', 'Milligrams'),
        ('g', 'Grams'),
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
        ('units', 'Units'),
        ('drops', 'Drops'),
        ('puffs', 'Puffs'),
        ('pieces', 'Pieces'),
        ('tablets', 'Tablets'),
        ('capsules', 'Capsules'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='attributes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    form = models.CharField(max_length=50, choices=FORM_CHOICES, default='tablet')
    composition = models.JSONField(default=dict, help_text="Flexible JSON for medicine composition details")
    dose = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    dose_unit = models.CharField(max_length=20, choices=DOSE_UNIT_CHOICES, default='mg')
    
    # Optional link to schedule if this attribute is schedule-specific
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, blank=True, null=True, related_name='attributes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['medicine']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.medicine.name} - {self.dose}{self.dose_unit} ({self.form})"


class Schedule(models.Model):
    """When to take medicine - supports RRULE for recurrence"""
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='schedules')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    timezone = models.CharField(max_length=100, default='Asia/Kathmandu')
    time = models.TimeField()  # Time of day to take medicine
    date = models.DateField()  # Start date
    end_date = models.DateField(blank=True, null=True)  # End date for schedule
    
    # RFC5545 RRULE for recurrence (optional)
    rrule = models.TextField(blank=True, null=True, help_text="RFC5545 RRULE for recurrence")
    
    instruction = models.TextField(blank=True, null=True, help_text="Instructions like 'after meal', 'before sleep'")
    
    # Dose overrides for this schedule
    dose_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    dose_unit = models.CharField(max_length=20, choices=MedicineAttribute.DOSE_UNIT_CHOICES, blank=True, null=True)
    dose = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])  # Alternative dose field
    
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time', 'date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['medicine']),
            models.Index(fields=['user', 'medicine']),
            models.Index(fields=['date', 'time']),
        ]

    def __str__(self):
        return f"{self.medicine.name} at {self.time} on {self.date}"


class Reminder(models.Model):
    """Scheduled notifications derived from Schedule"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('triggered', 'Triggered'),
        ('snoozed', 'Snoozed'),
        ('taken', 'Taken'),
        ('missed', 'Missed'),
        ('dismissed', 'Dismissed'),
        ('inactive', 'Inactive'),
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='reminders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Critical: next UTC timestamp to trigger (main index for worker)
    next_run = models.DateTimeField(db_index=True)
    snooze_until = models.DateTimeField(blank=True, null=True)
    triggered_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['next_run']
        indexes = [
            models.Index(fields=['next_run'], condition=models.Q(status='pending'), name='pending_reminders_idx'),
            models.Index(fields=['schedule']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Reminder for {self.schedule.medicine.name} at {self.next_run}"


class Intake(models.Model):
    """Record when a user confirms medication intake or misses it"""
    
    STATUS_CHOICES = [
        ('taken', 'Taken'),
        ('missed', 'Missed'),
        ('partial', 'Partial'),
        ('skipped', 'Skipped'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intakes')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='intakes')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, blank=True, null=True, related_name='intakes')
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, blank=True, null=True, related_name='intakes')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    scheduled_time = models.DateTimeField()  # When it was supposed to be taken
    taken_at = models.DateTimeField(blank=True, null=True)  # When it was actually taken
    
    # Who recorded this intake (user or caretaker)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recorded_intakes')
    
    # Actual dose taken (might differ from scheduled)
    actual_dose = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    actual_dose_unit = models.CharField(max_length=20, choices=MedicineAttribute.DOSE_UNIT_CHOICES, blank=True, null=True)
    
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-taken_at', '-scheduled_time']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['user', '-taken_at']),
            models.Index(fields=['medicine']),
            models.Index(fields=['scheduled_time']),
        ]

    def __str__(self):
        return f"{self.medicine.name} - {self.status} at {self.taken_at or self.scheduled_time}"
