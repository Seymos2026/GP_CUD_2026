#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Render's free tier has no shell, so the admin account is created here.
# Safe to re-run: it updates the existing account instead of failing.
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
from accounts.models import Student, Faculty

User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ['DJANGO_SUPERUSER_PASSWORD']

# role must be set in defaults: the post_save signal in accounts/signals.py
# creates a Student/Faculty profile based on the role at creation time.
user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'role': User.Role.ADMIN,
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'must_change_password': False,
    },
)

if not created:
    user.email = email
    user.role = User.Role.ADMIN
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True

user.set_password(password)
user.save()

# Clean up profiles wrongly attached to the admin by an earlier deploy.
removed = Student.objects.filter(user=user).delete()[0] + Faculty.objects.filter(user=user).delete()[0]

print('Superuser created.' if created else 'Superuser updated.')
if removed:
    print('Removed %d stray profile(s) from the admin account.' % removed)
"
fi
