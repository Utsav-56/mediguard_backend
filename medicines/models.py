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
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="medicines", help_text="User who owns this medicine")

    name = models.CharField(max_length=255, help_text="Name of the medicine")
    description = models.TextField(blank=True, null=True, help_text="Description of the medicine")

    # dose of medicine like mg, ml, etc
    dose = models.CharField(max_length=50, help_text="Dose of the medicine (e.g., 500mg, 10ml)")

    # does unit means the no of tablets or syrups or injections
    dose_unit = models.CharField(max_length=50, help_text="Unit of the dose (e.g., 5 , 10)")

    # days a week the medicine is taken stored in an jsonb array of integers e.g [1,2,3] means monday, tuesday, wednesday
    days_a_week = models.JSONField(help_text="Days of the week the medicine is taken (e.g., [1,2,3] for Mon, Tue, Wed)")

    # time of day when the medicine is taken stored in an jsonb array of strings e.g ["8:00", "12:00"] means 8:00 am, 12:00 pm etc in 24-hour format
    time_of_day = models.JSONField(help_text="Time of day when the medicine is taken (e.g., ['8:00', '12:00']) in 24-hour format")

    # additional composition map if any or else can be blank
    composition = models.JSONField(blank=True, null=True, help_text="Additional composition details (e.g., {'paracetamol': '500mg', 'ingredient2': 'value2'})")

    image = models.ImageField(upload_to=medicine_image_path, blank=True, null=True, help_text="Image of the medicine if any or else can be blank")

    def __str__(self):
        return f"{self.name} ({self.dose} x {self.dose_unit}) for User {self.user.email}"

    class Meta:
        ordering = ["id"]
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"



# serialisers for medicines

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicines
        fields = "__all__"
        read_only_fields = ["user"]



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
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="intakes", help_text="User who owns this intake")

    # medicine id who owns this intake relation to medicines.Medicines model
    medicine = models.ForeignKey("medicines.Medicines", on_delete=models.CASCADE, related_name="intakes", help_text="Medicine who owns this intake")

    # status of the intake like taken, skipped, missed, etc
    INTAKE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("taken", "Taken"),
        ("skipped", "Skipped"),
        ("missed", "Missed"),
    ]
    status = models.CharField(max_length=50, choices=INTAKE_STATUS_CHOICES, help_text="Status of the intake (e.g., taken, skipped, missed)")

    def __str__(self):
        return f"{self.medicine.name} ({self.status}) for User {self.user.email}"

    class Meta:
        ordering = ["id"]
        verbose_name = "Intake"
        verbose_name_plural = "Intakes"

