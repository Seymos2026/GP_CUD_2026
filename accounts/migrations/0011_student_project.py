"""Move student assignment from Team to Project directly.

Team was a one-to-one pass-through on Project that only carried a name, so a
student's team already implied exactly one project. This adds Student.project,
copies the assignment across, then drops Student.team. The Team model itself is
removed in projects/0005, which depends on this migration.
"""
from django.db import migrations, models
import django.db.models.deletion


def team_to_project(apps, schema_editor):
    """Point each student at the project their team belonged to."""
    Student = apps.get_model("accounts", "Student")
    moved = 0
    for student in Student.objects.filter(team__isnull=False).select_related("team"):
        student.project_id = student.team.project_id
        student.save(update_fields=["project"])
        moved += 1
    if moved:
        print(f"    migrated {moved} student assignment(s) from team to project")


def project_to_team(apps, schema_editor):
    """Reverse: rebuild one team per project and reattach students."""
    Student = apps.get_model("accounts", "Student")
    Team = apps.get_model("projects", "Team")
    for student in Student.objects.filter(project__isnull=False):
        team, _ = Team.objects.get_or_create(project_id=student.project_id)
        student.team_id = team.id
        student.save(update_fields=["team"])


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_weeklyprogress_weeklyattendance"),
        ("accounts", "0010_user_must_change_password"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="students",
                to="projects.project",
                help_text="Graduation project this student is assigned to",
            ),
        ),
        migrations.RunPython(team_to_project, project_to_team),
        migrations.RemoveField(model_name="student", name="team"),
    ]
