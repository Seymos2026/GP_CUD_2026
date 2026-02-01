"""
Signals to automatically create Student/Faculty profiles when Users are created
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Faculty


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create Student or Faculty profile when a User is created with the corresponding role
    """
    if created:
        if instance.role == User.Role.STUDENT:
            # Create Student profile if it doesn't exist
            Student.objects.get_or_create(
                user=instance,
                defaults={'student_id': f"STU-{instance.id:04d}"}
            )
        elif instance.role == User.Role.FACULTY:
            # Create Faculty profile if it doesn't exist
            Faculty.objects.get_or_create(
                user=instance,
                defaults={'faculty_id': f"FAC-{instance.id:04d}"}
            )
