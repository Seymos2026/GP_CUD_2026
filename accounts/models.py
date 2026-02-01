from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access"""
    
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        FACULTY = "FACULTY", "Faculty"
    
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_staff
    
    def is_faculty(self):
        return self.role == self.Role.FACULTY
    
    def is_student_user(self):
        return self.role == self.Role.STUDENT


class Faculty(models.Model):
    """Faculty profile linked to User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile")
    faculty_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Faculty"
        verbose_name_plural = "Faculty"
        ordering = ["faculty_id", "user__last_name"]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.faculty_id or 'N/A'})"


class Student(models.Model):
    """Student profile linked to User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    major = models.CharField(max_length=200, blank=True, null=True, help_text="Student's major field of study")
    team = models.ForeignKey("projects.Team", on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["student_id", "user__last_name"]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.student_id or 'No ID'})"
    
    def save(self, *args, **kwargs):
        """Auto-generate student_id if not provided"""
        if not self.student_id:
            # Generate student_id from username or user ID
            if self.user:
                self.student_id = f"STU-{self.user.id:04d}" if self.user.id else f"STU-{self.user.username.upper()}"
        super().save(*args, **kwargs)
