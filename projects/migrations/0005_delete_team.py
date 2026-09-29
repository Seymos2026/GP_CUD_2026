"""Remove the Team model.

Students now point at Project directly (accounts/0011), so Team no longer
carries anything: it was one-to-one with Project and held only a name.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_weeklyprogress_weeklyattendance"),
        ("accounts", "0011_student_project"),
    ]

    operations = [
        migrations.DeleteModel(name="Team"),
    ]
