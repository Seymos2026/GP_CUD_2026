from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from projects.models import Project, FacultyProjectAssignment
from accounts.models import Faculty
from rubrics.models import Criterion


class Evaluation(models.Model):
    """Faculty member's evaluation for a project (only for faculty assigned as Judge)"""
    
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="evaluations")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="evaluations", null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     help_text="Calculated total score")
    comments = models.TextField(blank=True, null=True, help_text="General comments from judge")
    judge_signature = models.CharField(max_length=200, blank=True, null=True, help_text="Judge signature/name")
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evaluation"
        verbose_name_plural = "Evaluations"
        ordering = ["-created_at"]
        unique_together = [["project", "faculty"]]
    
    def __str__(self):
        return f"{self.faculty.user.username} - {self.project.title} ({self.status})"
    
    def clean(self):
        """Validate that faculty is assigned as Judge (not Supervisor) for this project"""
        if self.project and self.faculty:
            # Check if faculty is assigned as Judge for this project
            assignment = FacultyProjectAssignment.objects.filter(
                project=self.project,
                faculty=self.faculty
            ).first()
            
            if not assignment:
                raise ValidationError({
                    'faculty': 'This faculty member is not assigned to this project.'
                })
            
            if assignment.role != FacultyProjectAssignment.Role.JUDGE:
                raise ValidationError({
                    'faculty': f'This faculty member is assigned as {assignment.get_role_display()} for this project. Only faculty assigned as Judge can create evaluations.'
                })
    
    def save(self, *args, **kwargs):
        # Round total_score to 2 decimal places if it's set
        if self.total_score is not None:
            from decimal import Decimal, ROUND_HALF_UP
            self.total_score = Decimal(str(self.total_score)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.full_clean()
        super().save(*args, **kwargs)
    
    def calculate_total_score(self, student=None):
        """Calculate total score from all criterion scores for a specific student or team average"""
        from decimal import Decimal, ROUND_HALF_UP
        
        if student:
            scores = self.scores.filter(student=student)
        else:
            # Calculate average across all students for team-level score
            scores = self.scores.all()
        
        if not scores.exists():
            return Decimal('0.00')
        
        total = Decimal('0.00')
        for score in scores:
            criterion = score.criterion
            weighted_score = Decimal(str(score.score)) * Decimal(str(criterion.weight))
            total += weighted_score
        
        if not student:
            # Average across students if team-level
            student_count = scores.values('student').distinct().count()
            if student_count > 0:
                total = total / Decimal(str(student_count))
        
        # Round to 2 decimal places to match the field definition
        total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.total_score = total
        self.save(update_fields=["total_score"])
        return total
    
    def get_all_criteria_scores(self):
        """Get all scores for this evaluation, including missing criteria"""
        rubric = self.project.rubric
        if not rubric:
            return []
        
        scores_dict = {score.criterion_id: score for score in self.scores.all()}
        result = []
        for criterion in rubric.criteria.all():
            score_obj = scores_dict.get(criterion.id)
            result.append({
                'criterion': criterion,
                'score': score_obj,
                'has_score': score_obj is not None
            })
        return result


class Score(models.Model):
    """Individual score for a criterion within an evaluation, per student"""
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name="scores")
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name="scores")
    student = models.ForeignKey("accounts.Student", on_delete=models.CASCADE, related_name="scores", null=True, blank=True,
                                help_text="Student being scored (null for team-level scores)")
    score = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(0)],
                               help_text="Score given for this criterion")
    comments = models.TextField(blank=True, null=True, help_text="Criterion-specific feedback")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Score"
        verbose_name_plural = "Scores"
        ordering = ["evaluation", "student", "criterion__order"]
        unique_together = [["evaluation", "criterion", "student"]]
    
    def __str__(self):
        return f"{self.evaluation.faculty.user.username} - {self.criterion.name}: {self.score}"
    
    def clean(self):
        """Validate score doesn't exceed max_score"""
        from django.core.exceptions import ValidationError
        if self.score is not None and self.criterion and self.score > self.criterion.max_score:
            raise ValidationError(
                f"Score ({self.score}) cannot exceed maximum score ({self.criterion.max_score}) for this criterion."
            )
    
    def save(self, *args, **kwargs):
        """Override save to validate"""
        self.full_clean()
        super().save(*args, **kwargs)
        # Don't recalculate total_score automatically since we're scoring per-student
        # Total scores are calculated per-student in reports, not at evaluation level
