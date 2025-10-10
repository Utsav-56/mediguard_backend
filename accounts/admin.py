from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Caretaker, UserCaretaker


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'phone_number', 'timezone', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'timezone')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number', 'address', 'timezone', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )


@admin.register(Caretaker)
class CaretakerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'phone_number', 'email')
    ordering = ('-created_at',)


@admin.register(UserCaretaker)
class UserCaretakerAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'caretaker', 'can_view_medicines', 'can_add_medicines', 
        'can_confirm_intakes', 'created_at'
    )
    list_filter = (
        'can_view_medicines', 'can_add_medicines', 'can_edit_medicines',
        'can_delete_medicines', 'can_view_health_metrics', 'can_confirm_intakes',
        'created_at'
    )
    search_fields = ('user__full_name', 'caretaker__full_name')
    ordering = ('-created_at',)
