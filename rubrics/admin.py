from django.contrib import admin
from .models import Rubric, Criterion


class CriterionInline(admin.TabularInline):
    """Inline admin for Criterion within Rubric"""
    model = Criterion
    extra = 1
    fields = ['name', 'description', 'weight', 'max_score', 'order']
    ordering = ['order']


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    """Admin interface for Rubric model"""
    list_display = ['name', 'max_total_score', 'criterion_count', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    autocomplete_fields = ['created_by']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CriterionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'max_total_score')
        }),
        ('File Information', {
            'fields': ('file_path',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def criterion_count(self, obj):
        """Display number of criteria"""
        return obj.criteria.count()
    criterion_count.short_description = 'Criteria'


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    """Admin interface for Criterion model"""
    list_display = ['name', 'rubric', 'section_title', 'max_score', 'weight', 'order']
    list_filter = ['rubric', 'section_title', 'created_at']
    search_fields = ['name', 'description', 'rubric__name', 'section_title']
    autocomplete_fields = ['rubric']
    readonly_fields = ['created_at']
    ordering = ['rubric', 'order']
    fields = ['rubric', 'section_title', 'name', 'description', 'max_score', 'weight', 'order', 'created_at']