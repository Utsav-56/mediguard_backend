from django.contrib import admin
from .models import Medicine, MedicineAttribute, Schedule, Reminder, Intake


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'user', 'start_date', 'until', 'created_at')
    list_filter = ('start_date', 'until', 'created_at')
    search_fields = ('name', 'brand', 'user__full_name', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MedicineAttribute)
class MedicineAttributeAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'form', 'dose', 'dose_unit', 'user', 'created_at')
    list_filter = ('form', 'dose_unit', 'created_at')
    search_fields = ('medicine__name', 'user__full_name')
    ordering = ('-created_at',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'user', 'time', 'date', 'end_date', 'timezone')
    list_filter = ('date', 'end_date', 'timezone', 'created_at')
    search_fields = ('medicine__name', 'user__full_name', 'instruction')
    ordering = ('date', 'time')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'status', 'next_run', 'triggered_at', 'resolved_at')
    list_filter = ('status', 'next_run', 'triggered_at', 'created_at')
    search_fields = ('schedule__medicine__name', 'schedule__user__full_name')
    ordering = ('next_run',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Intake)
class IntakeAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'user', 'status', 'scheduled_time', 'taken_at', 'recorded_by')
    list_filter = ('status', 'taken_at', 'scheduled_time', 'created_at')
    search_fields = ('medicine__name', 'user__full_name', 'recorded_by__full_name')
    ordering = ('-taken_at', '-scheduled_time')
    readonly_fields = ('created_at', 'updated_at')
