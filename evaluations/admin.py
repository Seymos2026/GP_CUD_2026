from django.contrib import admin
from .models import Evaluation, Score


class ScoreInline(admin.TabularInline):
    """Inline admin for Score within Evaluation"""
    model = Score
    extra = 0
    fields = ['criterion', 'student', 'score', 'comments']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['criterion', 'student']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Admin interface for Evaluation model"""
    list_display = ['project', 'faculty', 'status', 'total_score', 'submitted_at', 'created_at']
    list_filter = ['status', 'created_at', 'submitted_at']
    search_fields = ['project__title', 'faculty__user__username', 'faculty__user__email']
    autocomplete_fields = ['project', 'faculty']
    readonly_fields = ['created_at', 'submitted_at', 'updated_at', 'total_score']
    inlines = [ScoreInline]
    
    fieldsets = (
        ('Evaluation Information', {
            'fields': ('project', 'faculty', 'status')
        }),
        ('Scores', {
            'fields': ('total_score',)
        }),
        ('Comments', {
            'fields': ('comments', 'judge_signature')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to calculate total score"""
        super().save_model(request, obj, form, change)
        if obj.status == Evaluation.Status.SUBMITTED and not obj.submitted_at:
            from django.utils import timezone
            obj.submitted_at = timezone.now()
            obj.save(update_fields=['submitted_at'])


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    """Admin interface for Score model"""
    list_display = ['evaluation', 'criterion', 'student', 'score', 'created_at']
    list_filter = ['created_at', 'criterion__rubric', 'student']
    search_fields = ['evaluation__project__title', 'criterion__name', 'student__user__username', 'comments']
    autocomplete_fields = ['evaluation', 'criterion', 'student']
    readonly_fields = ['created_at', 'updated_at']
