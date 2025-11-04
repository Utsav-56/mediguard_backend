from django.urls import path
from . import views

app_name = "image_processer"

urlpatterns = [
    path("process-image/", views.upload_and_process_image, name="process_image"),
    path(
        "analyse/", views.upload_and_process_image, name="upload_and_process_image"
    ),  # Optional: for testing
]
