from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Faculty, Student


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """Admin interface for Faculty model"""
    list_display = ['user', 'faculty_id', 'department', 'specialization', 'created_at']
    list_filter = ['created_at', 'department']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'faculty_id']
    autocomplete_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model"""
    list_display = ['user', 'student_id', 'major', 'team', 'created_at']
    list_filter = ['created_at', 'team', 'major']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'student_id', 'major']
    autocomplete_fields = ['user', 'team']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'student_id', 'major', 'team')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
