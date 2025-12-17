import json

from django.core.exceptions import ValidationError
from django.db import models


class HealthTemplate(models.Model):
    """
    Predefined templates for health metrics.

    Templates define the structure of health data that users can record.
    Only admins can create/edit/delete templates.
    Users can only read templates and create records based on them.
    """

    id = models.AutoField(primary_key=True, help_text="Unique ID for the template")

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the template (e.g., 'Blood Pressure', 'Blood Sugar')",
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier (e.g., 'blood-pressure')",
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of what this health metric measures",
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Icon identifier for frontend (e.g., 'heart', 'droplet')",
    )

    category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Category for grouping (e.g., 'cardiovascular', 'metabolic')",
    )

    # JSON schema defining the fields and their types
    # Format: {"field_name": {"type": "int|float|string|boolean", "unit": "mmHg", "min": 0, "max": 300, "required": true}}
    schema = models.JSONField(
        help_text="JSON schema defining fields, types, units, and validation rules"
    )

    # Normal range for reference (optional)
    normal_range = models.JSONField(
        blank=True,
        null=True,
        help_text="Normal/healthy ranges for each field (for display purposes)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this template is available for users"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "Health Template"
        verbose_name_plural = "Health Templates"

    def __str__(self):
        return self.name

    def validate_data(self, data):
        """
        Validate user-provided data against this template's schema.
        Returns (is_valid, errors) tuple.
        """
        errors = {}

        if not isinstance(data, dict):
            return False, {"data": "Must be a JSON object"}

        schema = self.schema

        # Check for required fields and validate types
        for field_name, field_config in schema.items():
            field_type = field_config.get("type", "string")
            is_required = field_config.get("required", True)
            min_val = field_config.get("min")
            max_val = field_config.get("max")

            # Check if required field is missing
            if field_name not in data:
                if is_required:
                    errors[field_name] = f"This field is required"
                continue

            value = data[field_name]

            # Allow null for non-required fields
            if value is None and not is_required:
                continue

            # Type validation
            if field_type == "int":
                if not isinstance(value, int) or isinstance(value, bool):
                    errors[field_name] = f"Must be an integer"
                    continue
            elif field_type == "float":
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    errors[field_name] = f"Must be a number"
                    continue
            elif field_type == "string":
                if not isinstance(value, str):
                    errors[field_name] = f"Must be a string"
                    continue
            elif field_type == "boolean":
                if not isinstance(value, bool):
                    errors[field_name] = f"Must be a boolean"
                    continue

            # Range validation for numeric types
            if field_type in ["int", "float"] and isinstance(value, (int, float)):
                if min_val is not None and value < min_val:
                    errors[field_name] = f"Must be at least {min_val}"
                if max_val is not None and value > max_val:
                    errors[field_name] = f"Must be at most {max_val}"

        # Check for extra fields not in schema
        for field_name in data.keys():
            if field_name not in schema:
                errors[field_name] = f"Unknown field"

        return len(errors) == 0, errors


class HealthRecord(models.Model):
    """
    User's health record based on a template.

    Each record stores actual health measurements for a user
    following the structure defined by a HealthTemplate.
    """

    id = models.AutoField(primary_key=True, help_text="Unique ID for the health record")

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="health_records",
        help_text="User who owns this health record",
    )

    template = models.ForeignKey(
        HealthTemplate,
        on_delete=models.PROTECT,  # Prevent template deletion if records exist
        related_name="records",
        help_text="Template this record is based on",
    )

    # The actual health data following the template schema
    data = models.JSONField(
        help_text="Health metric values following the template schema"
    )

    # When the measurement was taken (user-provided)
    recorded_at = models.DateTimeField(
        help_text="When the health measurement was taken"
    )

    # Optional notes
    notes = models.TextField(
        blank=True, null=True, help_text="Additional notes about this measurement"
    )

    # Location where measurement was taken (optional)
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Where the measurement was taken (e.g., 'Home', 'Clinic')",
    )

    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name = "Health Record"
        verbose_name_plural = "Health Records"

    def __str__(self):
        return f"{self.template.name} - {self.user.email} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validate data against template schema before saving"""
        if self.template and self.data:
            is_valid, errors = self.template.validate_data(self.data)
            if not is_valid:
                raise ValidationError({"data": errors})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
