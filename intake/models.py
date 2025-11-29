from django.db import models
from django.utils import timezone


class Intake(models.Model):
    """
    Intake model records medicine intake events.
    Each record represents a single scheduled intake of a medicine.
    """
    
    id = models.AutoField(primary_key=True, help_text="Unique ID for the intake record")

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="intakes",
        help_text="User who owns this intake record",
    )

    medicine = models.ForeignKey(
        "medicines.Medicines",
        on_delete=models.CASCADE,
        related_name="intakes",
        help_text="Medicine associated with this intake",
    )

    # The date when the medicine was/is scheduled to be taken
    scheduled_date = models.DateField(
        help_text="Date when the medicine is scheduled to be taken",
    )

    # The time when the medicine was expected to be taken (from medicine schedule)
    scheduled_time = models.TimeField(
        help_text="Expected time for the medicine intake (e.g., 08:00)",
    )

    # Status of the intake
    INTAKE_STATUS_CHOICES = [
        ("pending", "Pending"),      # Not yet time for intake
        ("taken", "Taken"),          # Medicine was taken
        ("skipped", "Skipped"),      # User intentionally skipped
        ("missed", "Missed"),        # Time passed, not marked as taken
    ]
    status = models.CharField(
        max_length=20,
        choices=INTAKE_STATUS_CHOICES,
        default="pending",
        help_text="Status of the intake (pending/taken/skipped/missed)",
    )

    # Actual time when the medicine was taken (only filled when status is 'taken')
    taken_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Actual datetime when the medicine was taken",
    )

    # Notes from the user about this intake
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about this intake (e.g., side effects, taken with food)",
    )

    # Auto timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated",
    )

    class Meta:
        ordering = ["-scheduled_date", "-scheduled_time"]
        verbose_name = "Intake"
        verbose_name_plural = "Intakes"
        # Ensure no duplicate intake records for same medicine, date, and time
        unique_together = ["user", "medicine", "scheduled_date", "scheduled_time"]

    def __str__(self):
        return f"{self.medicine.name} - {self.scheduled_date} {self.scheduled_time} ({self.status})"

    @property
    def is_late(self):
        """Check if the medicine was taken late"""
        if self.status == "taken" and self.taken_at:
            scheduled_datetime = timezone.make_aware(
                timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
            )
            return self.taken_at > scheduled_datetime
        return False

    @property
    def delay_minutes(self):
        """Calculate how many minutes late the medicine was taken"""
        if self.is_late and self.taken_at:
            scheduled_datetime = timezone.make_aware(
                timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
            )
            delta = self.taken_at - scheduled_datetime
            return int(delta.total_seconds() / 60)
        return 0
