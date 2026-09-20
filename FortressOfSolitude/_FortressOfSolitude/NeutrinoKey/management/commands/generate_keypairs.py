from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from _FortressOfSolitude.NeutrinoKey.models import UserKeyPair

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate RSA-4096 key pairs for users who do not have one.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email of the user to generate a key pair for.',
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='The user\'s raw password (needed to derive KEK/DEK for wrapping).',
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User with email {email} not found.'))
            return

        if UserKeyPair.objects.filter(user=user).exists():
            self.stdout.write(self.style.WARNING(
                f'{email} already has a key pair — skipping.'
            ))
            return

        UserKeyPair.generate_for_user(user, password.encode())
        self.stdout.write(self.style.SUCCESS(
            f'Generated RSA-4096 key pair for {email}.'
        ))
