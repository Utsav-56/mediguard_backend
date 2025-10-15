from django.contrib import admin
from .models import Medicines, Intakes

# Register your models here.

admin.site.register(Medicines)
admin.site.register(Intakes)