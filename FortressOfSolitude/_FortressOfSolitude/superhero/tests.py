"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2022
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from _FortressOfSolitude.NeutrinoKey.models import UserKeyPair

User = get_user_model()


class RegistrationKeyPairTest(TestCase):
    """Test that user registration creates an RSA key pair."""

    def test_new_user_gets_keypair_via_form(self):
        """
        When a user is created through the registration form's save,
        a UserKeyPair is generated for them.
        """
        from .forms import DailyPlanetSubscriber

        form_data = {
            'email': 'jimmy@dailyplanet.com',
            'first_name': 'Jimmy',
            'last_name': 'Olsen',
            'password1': 'f0rtr3ss_s0l1tud3!',
            'password2': 'f0rtr3ss_s0l1tud3!',
        }
        form = DailyPlanetSubscriber(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        # The user should now have a key pair
        self.assertTrue(
            UserKeyPair.objects.filter(user=user).exists(),
            "Registration should create a UserKeyPair for the new user"
        )
        keypair = UserKeyPair.objects.get(user=user)
        self.assertIn('BEGIN PUBLIC KEY', keypair.public_key_pem)

    def test_keypair_private_key_decryptable_with_registration_password(self):
        """The generated private key can be decrypted with the registration password."""
        from .forms import DailyPlanetSubscriber

        raw_password = 'f0rtr3ss_s0l1tud3!'
        form_data = {
            'email': 'perry@dailyplanet.com',
            'first_name': 'Perry',
            'last_name': 'White',
            'password1': raw_password,
            'password2': raw_password,
        }
        form = DailyPlanetSubscriber(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        keypair = UserKeyPair.objects.get(user=user)
        priv_pem = keypair.get_private_key(raw_password.encode())
        self.assertIn(b'BEGIN RSA PRIVATE KEY', priv_pem)


class RegistrationFolderTest(TestCase):
    """Test that user registration creates folder hierarchy."""

    def test_new_user_gets_folder_tree(self):
        """Registration creates root folder with default subfolders."""
        from _FortressOfSolitude.superhero.forms import DailyPlanetSubscriber
        from _FortressOfSolitude.organizer.models import UserFolder

        form_data = {
            'email': 'barry@starlab.com',
            'first_name': 'Barry',
            'last_name': 'Allen',
            'password1': 'sp33dst3r_2022!',
            'password2': 'sp33dst3r_2022!',
        }
        form = DailyPlanetSubscriber(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertTrue(
            UserFolder.objects.filter(owner=user, parent=None, name='root').exists()
        )
        root = UserFolder.objects.get(owner=user, parent=None)
        children = UserFolder.objects.filter(parent=root)
        self.assertEqual(children.count(), 5)
