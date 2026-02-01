from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from rubrics.models import Rubric


class FacultyProjectAssignment(models.Model):
    """Tracks faculty assignments to projects as either Judge or Supervisor"""
    
    class Role(models.TextChoices):
        JUDGE = "JUDGE", "Judge"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
    
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="faculty_assignments")
    faculty = models.ForeignKey("accounts.Faculty", on_delete=models.CASCADE, related_name="project_assignments")
    role = models.CharField(max_length=20, choices=Role.choices, help_text="Role of faculty member for this project")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Faculty Project Assignment"
        verbose_name_plural = "Faculty Project Assignments"
        unique_together = [["project", "faculty"]]
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.faculty.user.username} - {self.project.title} ({self.role})"
    
    def clean(self):
        """Validate that a faculty member cannot be both judge and supervisor for the same project"""
        if self.project and self.faculty:
            # Check if this faculty member already has a different role for this project
            existing = FacultyProjectAssignment.objects.filter(
                project=self.project,
                faculty=self.faculty
            ).exclude(pk=self.pk if self.pk else None).first()
            
            if existing:
                if existing.role != self.role:
                    raise ValidationError({
                        'role': f'This faculty member is already assigned as {existing.get_role_display()} for this project. A faculty member cannot be both Judge and Supervisor for the same project.'
                    })


class Project(models.Model):
    """Project entity"""
    
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        EVALUATING = "EVALUATING", "Evaluating"
        COMPLETED = "COMPLETED", "Completed"
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    rubric = models.ForeignKey(Rubric, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_projects")
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.title
    
    @property
    def supervisor(self):
        """Get the supervisor for this project from faculty assignments"""
        try:
            assignment = self.faculty_assignments.filter(role=FacultyProjectAssignment.Role.SUPERVISOR).first()
            return assignment.faculty.user if assignment else None
        except:
            return None
    
    @property
    def judges(self):
        """Get all judges for this project from faculty assignments"""
        assignments = self.faculty_assignments.filter(role=FacultyProjectAssignment.Role.JUDGE)
        return [assignment.faculty.user for assignment in assignments]
    
    def get_team(self):
        """Safely get the team associated with this project, returns None if no team exists"""
        try:
            return self.team
        except Team.DoesNotExist:
            return None
        except AttributeError:
            return None


class Team(models.Model):
    """Team entity - multiple students per team"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="team")
    team_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ["team_name", "-created_at"]
    
    def __str__(self):
        return self.team_name or f"Team for {self.project.title}"
    
    @property
    def members(self):
        """Get all students in this team"""
        return self.students.all()
