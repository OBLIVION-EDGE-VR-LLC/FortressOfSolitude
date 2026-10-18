"""
Grant default permissions to all existing users.
Run after permission expansion to update users created before the change.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()


class Command(BaseCommand):
    help = 'Grant default content permissions to all existing users'

    def handle(self, *args, **options):
        allowed_apps = ['organizer', 'Blog', 'agora', 'core', 'NeutrinoKey']
        default_perms = Permission.objects.filter(
            content_type__app_label__in=allowed_apps
        )
        users = User.objects.all()
        count = 0
        for user in users:
            user.user_permissions.add(*default_perms)
            count += 1
        self.stdout.write(self.style.SUCCESS(
            f'Granted {default_perms.count()} permissions to {count} users'
        ))
