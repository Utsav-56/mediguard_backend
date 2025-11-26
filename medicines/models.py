from django.db import models
from rest_framework import serializers


# medcine model contains all the medicines

def medicine_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/medicines/medicine_<id>/<filename>
    ext = filename.split(".")[-1]
    return f"medicines/medicine_{instance.id}.{ext}"


class Medicines(models.Model):
    # id will be primary key we using postgreSQl so it should be auto incrementing serial
    id = models.AutoField(primary_key=True, help_text="Unique ID for the medicine")

    # user id who owns this medicine relation to accounts.User model
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="medicines",
        help_text="User who owns this medicine",
    )

    name = models.CharField(max_length=255, help_text="Name of the medicine")
    
    # amount indicates the number of units of medicine to be taken at a time (e.g., 2 tablets, 1 syrup spoon)
    amount = models.IntegerField(
        help_text="Number of units to be taken at a time (e.g., 2 tablets)"
    )

    # dosage indicates the dosage of units of medicine to take (e.g., 500mg, 1ml)
    dosage = models.IntegerField(
        help_text="Dosage of the medicine (e.g., 500 for 500mg)"
    )

    # days a week the medicine is taken stored in an jsonb array of integers e.g [1,2,3,4,5,6,7] where 1=Sunday, 7=Saturday
    days_of_week = models.JSONField(
        help_text="Days of the week the medicine is taken (e.g., [1,2,3,4,5,6,7] for Sun-Sat)"
    )

    # time of day when the medicine is taken stored in an jsonb array of time strings e.g ["08:00", "14:00", "20:00"] in 24-hour format
    time = models.JSONField(
        help_text="Times of day when the medicine is taken (e.g., ['08:00', '14:00', '20:00']) in HH:MM format"
    )

    image = models.ImageField(
        upload_to=medicine_image_path,
        blank=True,
        null=True,
        help_text="Image of the medicine if any or else can be blank",
    )

    # help_message is an extra note set by the user for the user itself to remember
    help_message = models.TextField(
        blank=True,
        null=True,
        help_text="Extra note for the user to remember about this medicine"
    )

    # start_date indicates when the medicine schedule starts
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Start date of the medicine schedule"
    )

    # end_date indicates when the medicine schedule ends
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="End date of the medicine schedule"
    )


    def __str__(self):
        return f"{self.name} ({self.amount} units x {self.dosage}mg) for User {self.user.email}"

    class Meta:
        ordering = ["id"]
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"


# serialisers for medicines


class MedicineSerializer(serializers.ModelSerializer):
    # Make image_url return the full URL instead of just the path
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Medicines
        fields = [
            "id",
            "name",
            "amount",
            "dosage",
            "time",
            "days_of_week",
            "image_url",
            "help_message",
            "start_date",
            "end_date",
        ]
        read_only_fields = ["user", "id"]

    def get_image_url(self, obj):
        """Return the full URL for the image if it exists"""
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def to_representation(self, instance):
        """Customize the output format"""
        representation = super().to_representation(instance)
        # Ensure time and days_of_week are lists (not dicts)
        if representation.get('time'):
            representation['time'] = list(representation['time'])
        if representation.get('days_of_week'):
            representation['days_of_week'] = list(representation['days_of_week'])
        return representation




# Intakes model contains all the intakes
# it is auto populated before 5 mins of the time_of_day in needed days of week
# to save unnecessary data we will only store intakes  of those whose staus is taken or skipped
# for other statuses we handle it in frontend itself by comparing the  created at of medicines
# and the time_of_day and days_a_week of the medicines
#
#  Plan is to run a cron job every day at midnight to populate the intakes for the day
class Intakes(models.Model):
    # id will be primary key we using postgreSQl so it should be auto incrementing serial
    id = models.AutoField(primary_key=True, help_text="Unique ID for the intake")

    # user id who owns this intake relation to accounts.User model
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="intakes",
        help_text="User who owns this intake",
    )

    # medicine id who owns this intake relation to medicines.Medicines model
    medicine = models.ForeignKey(
        "medicines.Medicines",
        on_delete=models.CASCADE,
        related_name="intakes",
        help_text="Medicine who owns this intake",
    )

    # status of the intake like taken, skipped, missed, etc
    INTAKE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("taken", "Taken"),
        ("skipped", "Skipped"),
        ("missed", "Missed"),
    ]
    status = models.CharField(
        max_length=50,
        choices=INTAKE_STATUS_CHOICES,
        help_text="Status of the intake (e.g., taken, skipped, missed)",
    )

    def __str__(self):
        return f"{self.medicine.name} ({self.status}) for User {self.user.email}"

    class Meta:
        ordering = ["id"]
        verbose_name = "Intake"
        verbose_name_plural = "Intakes"
