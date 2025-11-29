from django.contrib import admin
from .models import Intake


@admin.register(Intake)
class IntakeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'medicine',
        'scheduled_date',
        'scheduled_time',
        'status',
        'taken_at',
        'created_at',
    ]
    list_filter = ['status', 'scheduled_date', 'medicine']
    search_fields = ['user__email', 'medicine__name', 'notes']
    ordering = ['-scheduled_date', '-scheduled_time']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'medicine')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'scheduled_time')
        }),
        ('Status', {
            'fields': ('status', 'taken_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
