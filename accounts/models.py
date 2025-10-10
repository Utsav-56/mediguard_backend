from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone as django_timezone


def user_profile_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profile_images/user_<id>/<filename>
    ext = filename.split(".")[-1]
    return f"profile_images/user_{instance.id}.{ext}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=100, default='Asia/Kathmandu')

    profile_image = models.ImageField(
        upload_to=user_profile_image_path, blank=True, null=True
    )  # ✅ Added

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=django_timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def save(self, *args, **kwargs):
        # first save to generate ID
        if not self.id:
            saved_image = self.profile_image
            self.profile_image = None
            super().save(*args, **kwargs)
            self.profile_image = saved_image

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(" ")[0]


class Caretaker(models.Model):
    """Person who can help a user - stored as its own table"""
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class UserCaretaker(models.Model):
    """Link table between user and caretaker with permission flags"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_caretakers')
    caretaker = models.ForeignKey(Caretaker, on_delete=models.CASCADE, related_name='caretaker_users')
    
    # Permission flags
    can_view_medicines = models.BooleanField(default=True)
    can_add_medicines = models.BooleanField(default=False)
    can_edit_medicines = models.BooleanField(default=False)
    can_delete_medicines = models.BooleanField(default=False)
    can_view_health_metrics = models.BooleanField(default=True)
    can_add_health_metrics = models.BooleanField(default=False)
    can_confirm_intakes = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'caretaker')

    def __str__(self):
        return f"{self.user.full_name} -> {self.caretaker.full_name}"
