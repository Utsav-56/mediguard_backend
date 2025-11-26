from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.medicines_list, name="list_medicines"),
    path("add/", views.medicines_add, name="add_medicine"),
    path("detail/<int:medicine_id>/", views.medicine_detail, name="medicine_detail"),
    path("update/<int:medicine_id>/", views.medicine_update, name="update_medicine"),
    path("delete/<int:medicine_id>/", views.medicine_delete, name="delete_medicine"),
]
