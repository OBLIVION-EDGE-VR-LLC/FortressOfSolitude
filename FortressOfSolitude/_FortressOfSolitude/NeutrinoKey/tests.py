"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2021
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import (
    UserKeyPair, KEK, DEK, CryptoTools,
    secure_erase_bytes,
)

User = get_user_model()


class UserKeyPairModelTest(TestCase):
    """Tests for the UserKeyPair model and RSA key pair lifecycle."""

    def setUp(self):
        # Use model.objects.create + set_password to avoid the custom
        # UserManager's group-assignment logic which fails before save().
        self.user = User(email='clark@dailyplanet.com', is_active=True)
        self.user.set_password('krypt0n_r0cks_2022!')
        self.user.save(using='default')
        self.password = b'krypt0n_r0cks_2022!'

    def test_generate_for_user_creates_keypair(self):
        """Generating a key pair for a user stores it in the database."""
        keypair = UserKeyPair.generate_for_user(
            self.user, self.password
        )
        self.assertIsNotNone(keypair.pk)
        self.assertEqual(keypair.user, self.user)
        self.assertIn(b'BEGIN PUBLIC KEY', keypair.public_key_pem.encode())
        self.assertIsNotNone(keypair.encrypted_private_key)
        self.assertIsNotNone(keypair.private_key_nonce)
        self.assertIsNotNone(keypair.kek)
        self.assertIsNotNone(keypair.dek)

    def test_generate_creates_one_to_one_with_user(self):
        """Only one key pair per user is allowed."""
        UserKeyPair.generate_for_user(self.user, self.password)
        # Fetching by user should return the same one
        fetched = UserKeyPair.objects.get(user=self.user)
        self.assertEqual(fetched.user.email, 'clark@dailyplanet.com')


class UserKeyPairCryptoTest(TestCase):
    """Tests for RSA key pair encryption/decryption round-trip."""

    def setUp(self):
        # Use direct instantiation to avoid the custom UserManager's
        # group-assignment logic which fails before save().
        self.user = User(email='lois@dailyplanet.com', is_active=True)
        self.user.set_password('m3tr0p0l1s_2022!')
        self.user.save(using='default')
        self.password = b'm3tr0p0l1s_2022!'
        self.keypair = UserKeyPair.generate_for_user(
            self.user, self.password
        )

    def test_private_key_decrypts_to_valid_pem(self):
        """Decrypted private key is valid PEM format."""
        priv_pem = self.keypair.get_private_key(self.password)
        self.assertIn(b'BEGIN RSA PRIVATE KEY', priv_pem)
        secure_erase_bytes(priv_pem)

    def test_wrong_password_fails_decryption(self):
        """Using the wrong password to decrypt the private key raises an error."""
        with self.assertRaises(Exception):
            self.keypair.get_private_key(b'wrong_password_entirely')

    def test_public_key_is_valid_pem(self):
        """Public key returns valid PEM bytes."""
        pub_pem = self.keypair.get_public_key()
        self.assertIn(b'BEGIN PUBLIC KEY', pub_pem)

    def test_rsa_encrypt_decrypt_round_trip(self):
        """Data encrypted with the public key can be decrypted with the private key."""
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_OAEP

        pub_pem = self.keypair.get_public_key()
        pub_key = RSA.import_key(pub_pem)

        priv_pem = self.keypair.get_private_key(self.password)
        priv_key = RSA.import_key(priv_pem)

        # Encrypt with public key
        cipher_enc = PKCS1_OAEP.new(pub_key)
        plaintext = b'Kryptonite is stored in vault 7'
        ciphertext = cipher_enc.encrypt(plaintext)

        # Decrypt with private key
        cipher_dec = PKCS1_OAEP.new(priv_key)
        decrypted = cipher_dec.decrypt(ciphertext)

        self.assertEqual(plaintext, decrypted)

        secure_erase_bytes(priv_pem)

    def test_encrypt_dek_with_public_key_round_trip(self):
        """
        Simulate the proxy re-encryption use case:
        encrypt a DEK with the recipient's public key,
        decrypt it with their private key.
        """
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_OAEP

        # Simulate a 32-byte DEK (what we'd wrap for sharing)
        crypto = CryptoTools()
        fake_dek = crypto.RandomKey256()

        pub_key = RSA.import_key(self.keypair.get_public_key())
        cipher_enc = PKCS1_OAEP.new(pub_key)
        wrapped_dek = cipher_enc.encrypt(fake_dek)

        priv_pem = self.keypair.get_private_key(self.password)
        priv_key = RSA.import_key(priv_pem)
        cipher_dec = PKCS1_OAEP.new(priv_key)
        unwrapped_dek = cipher_dec.decrypt(wrapped_dek)

        self.assertEqual(fake_dek, unwrapped_dek)

        secure_erase_bytes(priv_pem)


from django.test import Client


class PublicKeyRetrievalTest(TestCase):
    """Tests for the public key lookup endpoint."""

    def setUp(self):
        # Use direct instantiation to avoid the custom UserManager's
        # group-assignment logic which fails before save().
        self.user = User(email='bruce@waynetech.com', is_active=True)
        self.user.set_password('g0tham_kn1ght!')
        self.user.save(using='default')
        self.keypair = UserKeyPair.generate_for_user(
            self.user, b'g0tham_kn1ght!'
        )
        self.requester = User(email='diana@themyscira.org', is_active=True)
        self.requester.set_password('amaz0n_pr1nc3ss!')
        self.requester.save(using='default')
        self.client = Client()
        self.client.login(email='diana@themyscira.org', password='amaz0n_pr1nc3ss!')

    def test_retrieve_existing_user_public_key(self):
        """Looking up an existing user's public key returns their PEM."""
        response = self.client.get('/keys/public/', {'email': 'bruce@waynetech.com'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('public_key', data)
        self.assertIn('BEGIN PUBLIC KEY', data['public_key'])

    def test_retrieve_nonexistent_user_returns_404(self):
        """Looking up a non-existent email returns 404 with no user info leak."""
        response = self.client.get('/keys/public/', {'email': 'nobody@nowhere.com'})
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_request_redirects(self):
        """Unauthenticated requests are redirected to login."""
        anon_client = Client()
        response = anon_client.get('/keys/public/', {'email': 'bruce@waynetech.com'})
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_missing_email_param_returns_400(self):
        """Requests without an email parameter return 400."""
        response = self.client.get('/keys/public/')
        self.assertEqual(response.status_code, 400)


from django.core.management import call_command
from io import StringIO


class GenerateKeypairsCommandTest(TestCase):
    """Tests for the generate_keypairs management command."""

    def test_command_generates_keypair_for_user_without_one(self):
        """The command generates a key pair for a specified user."""
        user = User(email='hal@oa.com', is_active=True)
        user.set_password('gr33n_l4nt3rn!')
        user.save(using='default')
        self.assertFalse(UserKeyPair.objects.filter(user=user).exists())

        out = StringIO()
        call_command(
            'generate_keypairs',
            '--email', 'hal@oa.com',
            '--password', 'gr33n_l4nt3rn!',
            stdout=out,
        )

        self.assertTrue(UserKeyPair.objects.filter(user=user).exists())
        self.assertIn('Generated', out.getvalue())

    def test_command_skips_user_who_already_has_keypair(self):
        """The command skips users who already have a key pair."""
        user = User(email='barry@starlab.com', is_active=True)
        user.set_password('sp33dst3r!')
        user.save(using='default')
        UserKeyPair.generate_for_user(user, b'sp33dst3r!')

        out = StringIO()
        call_command(
            'generate_keypairs',
            '--email', 'barry@starlab.com',
            '--password', 'sp33dst3r!',
            stdout=out,
        )
        self.assertIn('already has', out.getvalue())
