from django.db import models
from django.conf import settings


class Rubric(models.Model):
    """Evaluation rubric containing multiple criteria"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    max_total_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                         help_text="Maximum possible total score")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_rubrics")
    file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to original Excel file")
    
    class Meta:
        verbose_name = "Rubric"
        verbose_name_plural = "Rubrics"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.name
    
    def calculate_max_total_score(self):
        """Calculate max total score from criteria if not set"""
        if self.max_total_score:
            return self.max_total_score
        total = sum(criterion.max_score * criterion.weight for criterion in self.criteria.all())
        return total


class Criterion(models.Model):
    """Individual criterion within a rubric"""
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name="criteria")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, 
                                help_text="Weight for weighted scoring (default: 1.0)")
    max_score = models.DecimalField(max_digits=10, decimal_places=2, 
                                   help_text="Maximum score for this criterion")
    order = models.IntegerField(default=0, help_text="Order of criterion in rubric")
    section_title = models.CharField(max_length=200, blank=True, null=True,
                                    help_text="Section title (e.g., 'Midterm Presentation (Group)') - editable for organizing criteria")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Criterion"
        verbose_name_plural = "Criteria"
        ordering = ["rubric", "order", "id"]
        unique_together = [["rubric", "order"]]
    
    def __str__(self):
        return f"{self.rubric.name} - {self.name}"
