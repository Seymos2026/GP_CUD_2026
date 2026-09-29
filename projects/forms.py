"""Forms for the projects app."""
from django import forms

from .models import WeeklyProgress


class WeeklyProgressForm(forms.ModelForm):
    """The header of a weekly progress sheet. Attendance rows are handled in the view."""

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project

    def clean_week_number(self):
        """
        Enforce the (project, week_number) uniqueness here.

        ModelForm cannot do it for us: `project` is not a form field, so it is
        excluded from validate_unique and the clash only surfaces as an
        IntegrityError at save time.
        """
        week = self.cleaned_data["week_number"]
        if self.project is not None:
            clash = WeeklyProgress.objects.filter(project=self.project, week_number=week)
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                raise forms.ValidationError(
                    f"Week {week} already has a progress sheet for this project. "
                    f"Edit that sheet instead of creating a second one."
                )
        return week

    class Meta:
        model = WeeklyProgress
        fields = ["week_number", "meeting_date", "comments"]
        widgets = {
            "week_number": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 52,
            }),
            "meeting_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "comments": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "What the team covered this week, progress against the plan, "
                               "concerns, and actions agreed for next week.",
            }),
        }
        labels = {
            "week_number": "Week number",
            "meeting_date": "Meeting date",
            "comments": "Progress and performance notes",
        }
