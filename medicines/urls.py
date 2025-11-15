from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.medicines_list, name="list_medicines"),
    path("create/", views.medicines_create, name="create_medicine"),
    path("<int:medicine_id>/", views.medicine_detail, name="medicine_detail"),
    path("<int:medicine_id>/update/", views.medicine_update, name="update_medicine"),
    path("<int:medicine_id>/delete/", views.medicine_delete, name="delete_medicine"),
]
