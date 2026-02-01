from django.contrib import admin
from .models import Project, Team, FacultyProjectAssignment


class FacultyProjectAssignmentInline(admin.TabularInline):
    """Inline admin for Faculty Project Assignments within Project"""
    model = FacultyProjectAssignment
    extra = 1
    fields = ['faculty', 'role']
    autocomplete_fields = ['faculty']


@admin.register(FacultyProjectAssignment)
class FacultyProjectAssignmentAdmin(admin.ModelAdmin):
    """Admin interface for FacultyProjectAssignment model"""
    list_display = ['project', 'faculty', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['project__title', 'faculty__user__username', 'faculty__user__email']
    autocomplete_fields = ['project', 'faculty']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model"""
    list_display = ['title', 'rubric', 'get_supervisor', 'get_judges_count', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'rubric', 'created_at']
    search_fields = ['title', 'description']
    autocomplete_fields = ['rubric', 'created_by']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FacultyProjectAssignmentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'rubric', 'status')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_supervisor(self, obj):
        """Display supervisor from faculty assignments"""
        supervisor = obj.supervisor
        return supervisor.get_full_name() or supervisor.username if supervisor else "Not assigned"
    get_supervisor.short_description = 'Supervisor'
    
    def get_judges_count(self, obj):
        """Display count of judges"""
        return len(obj.judges)
    get_judges_count.short_description = 'Judges'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model"""
    list_display = ['team_name', 'project', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['team_name', 'project__title']
    autocomplete_fields = ['project']
    readonly_fields = ['created_at', 'updated_at']
    
    def member_count(self, obj):
        """Display number of team members"""
        return obj.students.count()
    member_count.short_description = 'Members'
