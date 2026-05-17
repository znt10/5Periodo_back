import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the default admin user."

    def handle(self, *args, **options):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@email.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "UNIFIP@123")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": "Admin",
            },
        )

        user.email = email
        user.first_name = user.first_name or "Admin"
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name="Gerente")
        user.groups.add(group)

        action = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(f"Default admin {action}: {email}")
        )
