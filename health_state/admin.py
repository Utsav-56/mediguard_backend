from django.contrib import admin
from .models import HealthTemplate, HealthRecord


@admin.register(HealthTemplate)
class HealthTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'slug',
        'category',
        'is_active',
        'created_at',
    ]
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'description', 'icon', 'category')
        }),
        ('Schema', {
            'fields': ('schema', 'normal_range'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'template',
        'recorded_at',
        'location',
        'created_at',
    ]
    list_filter = ['template', 'recorded_at', 'location']
    search_fields = ['user__email', 'template__name', 'notes']
    ordering = ['-recorded_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User & Template', {
            'fields': ('user', 'template')
        }),
        ('Health Data', {
            'fields': ('data', 'recorded_at', 'location', 'notes'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

