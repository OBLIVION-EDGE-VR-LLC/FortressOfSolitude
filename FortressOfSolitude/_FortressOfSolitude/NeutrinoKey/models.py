"""
DBA 1337_TECH, AUSTIN TEXAS © DECEMBER 2023
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from base64 import b64encode, b64decode
from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.contrib.auth import get_user_model
from django.db import models

from .cryptoutils import CryptoTools
import secrets

# Create your models here.

# Constants
LENGTH_OF_KEK = 32  # 256 bits or 32 bytes
LENGTH_OF_DEK = 32  # 256 bits or 32 bytes
LENGTH_OF_SALT = 32  # 256 bits or 32 bytes

'''
KeyMold is a models.Manager clas extension that includes creating a Kek and retrieving a kek
no inputs
'''


class KeyMold(models.Manager):

    def _create_kek(request, **kwargs):
        pwd = request.user.password
        self.kek = DeriveKek_default(pwd)
        return self.kek

    def get_queryset(self):
        qs = models.QuerySet(self.model)
        if self._db is not None:
            qs = qs.using('default')
        return qs


'''
TelescopeCoord is a models.Manager that allows to find the neutron star that will be used for the keyMold to make a Key Encryption Key [kek].
no inputs
'''


class TelescopeCoord(models.Manager):
    def get_queryset(self):
        qs = models.QuerySet(self.model)
        if self._db is not None:
            qs = qs.using('default')
        return qs


'''
QuasiPlasma is a models.Manager that allows for deriving Data Encryption Keys [DEKs] and retrieving deks from the neutron stars plasma.
no inputs
'''


class QuasiPlasma(models.Manager):

    def _create_dek(request, **kwargs):
        pwd = request.user.password
        self.dek = DeriveDek_default(pwd)
        return self.dek

    def get_queryset(self):
        qs = models.QuerySet(self.model)
        if self._db is not None:
            qs = qs.using('default')
        return qs


'''
KEK is the Key encryption Key [KEK] model.Model class extension that has the ability to derive a new KEK as well as wrap the KEK.
no inputs
'''


class KEK(models.Model):
    # Never should the key be passed as clear text always use the wrap or unwrap functions
    crypto = CryptoTools()
    kek = None
    wrappedKek = None
    result_wrapped_nonce = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))
    result_wrapped_kek = models.CharField(max_length=128, default=None)

    objects = TelescopeCoord()

    class Meta:
        verbose_name = 'KEK'

    def unwrap_key(self, password):
        if isinstance(password, str) and self.kek == None and self.wrappedKek == None:
            self.crypto.nonce = b64decode(self.result_wrapped_nonce)
            self.kek = self.crypto.AesDecryptEAX(b64decode(self.result_wrapped_kek),
                                                 self.crypto.Sha256(password.encode()))

        if isinstance(password, bytes) and self.kek == None and self.wrappedKek == None:
            if isinstance(self.result_wrapped_nonce, str):
                result_wrapped_nonce = (self.result_wrapped_nonce.encode()).replace(b"b'", b'')
                result_wrapped_nonce = result_wrapped_nonce[:-1]
                result_wrapped_nonce = result_wrapped_nonce + b'=' * (len(self.result_wrapped_nonce) % 4)
                self.crypto.nonce = b64decode(result_wrapped_nonce)
            else:
                self.crypto.nonce = b64decode(self.result_wrapped_nonce)
            if isinstance(self.result_wrapped_kek, str):
                result_wrapped_kek = (self.result_wrapped_kek.encode()).replace(b"b'", b'')

                result_wrapped_kek = result_wrapped_kek[:-1]

                result_wrapped_kek = result_wrapped_kek + b'=' * (len(result_wrapped_kek) % 4)
            elif isinstance(self.result_wrapped_kek, bytes):
                result_wrapped_kek = self.result_wrapped_kek
            self.kek = self.crypto.AesDecryptEAX(b64decode(result_wrapped_kek), CryptoTools().Sha256(password))


        else:
            try:
                self.crypto.nonce = b64decode(self.result_wrapped_nonce)
                if not isinstance(password, bytes):
                    password = password.encode()
                self.kek = self.crypto.AesDecryptEAX(b64decode(self.result_wrapped_kek), CryptoTools().Sha256(password))
                self.wrappedKek = None
            except:
                print('someone has attempted to spoof the KEK (key encryption key)')

        return self.kek

    def wrap_key(self, password):
        if isinstance(password, str) and self.kek == None:
            self.kek = self.crypto.AesEncryptEAX(data, self.crypto.Sha256(password.encode()))
            self.wrappedKek = self.kek
            secure_erase_bytes(self.kek)
            self.kek = None

        elif isinstance(password, bytes) and self.kek == None:
            self.kek = self.crypto.AesEncryptEAX(data, self.crypto.Sha256(password))
            self.wrappedKek = b64encode(self.kek)
            secure_erase_bytes(self.kek)
            self.kek = None
        elif self.kek != None:
            try:
                self.crypto.nonce = b64decode(self.result_wrapped_nonce)
                if isinstance(password, bytes):
                    self.wrappedKek = b64encode(self.crypto.AesEncryptEAX(self.kek, self.crypto.Sha256(password)))
                else:
                    self.wrappedKek = b64encode(
                        self.crypto.AesEncryptEAX(self.kek, self.crypto.Sha256(password.encode())))
                print("about to securely erase")
                secure_erase_bytes(self.kek)
                print("secureley erased")
                self.kek = None
            except OSError as ERROR:
                print('Wrapping KEK (key encryption key) was unsuccessful')

        return self.wrappedKek


'''
using the model of KEK unwrap and wrap the kek then unwrap the dek then pass the dek to a more useable object
perhaps this will also fetch the dek that is associated with that data model, so needs to be a manytomany relation.

DEK is a models.Model or Data Encryption Key class that allows to store, derive, and wrap Data Encryption Keys from a KEK and Salt
'''


class DEK(models.Model):
    crypto = CryptoTools()
    dek = None
    wrappedDek = None
    SALT = None
    result_wrapped_nonce = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))
    result_wrappedDek = models.CharField(max_length=128)

    result_SALT = models.CharField(max_length=45)
    kek_to_retrieve = models.ManyToManyField(KEK)

    objects = KeyMold()

    class Meta:
        verbose_name = 'DEK'

    @staticmethod
    def wrap_key_static(kek, password, key_to_wrap):
        crypto = CryptoTools()
        if isinstance(kek, KEK) and isinstance(key_to_wrap, str):
            kek.unwrap_key(password)
            crypto.nonce = b64decode(kek.result_wrapped_nonce)
            # strings are assumed to be base64 wrapped
            dek = crypto.AesEncryptEAX(b64decode(key_to_wrap), kek.key_to_wrap)
            kek.wrap_key(password)
            return dek

        elif isinstance(kek, KEK) and isinstance(key_to_wrap, bytes):
            kek.unwrap_key(password)

            crypto.nonce = b64decode(kek.result_wrapped_nonce)
            # bytes are assumed to be already base64decoded
            dek = crypto.AesEncryptEAX(key_to_wrap, kek.kek)
            kek.wrap_key(password)
            return dek

        else:
            try:
                kek.unwrap_key(password)
                self.crypto.nonce = b64decode(kek.result_wrapped_nonce)

                self.dek = self.crypto.AesEncryptEAX(self.result_wrappedDek, self.crypto.Sha256(kek.kek))
                kek.wrap_key(password)
                return self.dek

            except:
                print('someone has attempted to spoof the DEK (data encryption key)')

    def wrap_key(self, kek, password):
        if isinstance(kek, KEK) and isinstance(password, str):
            kek.unwrap_key(password)
            self.crypto.nonce = b64decode(kek.result_wrapped_nonce)
            self.dek = self.crypto.AesEncryptEAX(b64decode(self.result_wrappedDek), kek.kek)
            kek.wrap_key(password)
            return self.dek

        elif isinstance(kek, KEK) and isinstance(password, bytes):
            kek.unwrap_key(password)

            self.crypto.nonce = b64decode(kek.result_wrapped_nonce)

            self.dek = self.crypto.AesEncryptEAX(self.result_wrappedDek, kek.kek)
            kek.wrap_key(password)
            return self.dek

        else:
            try:
                kek.unwrap_key(password)
                self.crypto.nonce = b64decode(kek.result_wrapped_nonce)

                self.dek = self.crypto.AesEncryptEAX(self.result_wrappedDek, self.crypto.Sha256(kek.kek))
                kek.wrap_key(password)
                return self.dek

            except:
                print('someone has attempted to spoof the DEK (data encryption key)')

    def unwrap_key(self, kek, password):
        if isinstance(kek, KEK) and isinstance(password, str):
            master = kek.unwrap_key(password.encode())

            self.crypto.nonce = b64decode(self.result_wrapped_nonce)
            self.dek = self.crypto.AesDecryptEAX(b64decode(self.result_wrappedDek), self.crypto.Sha256(master))

            kek.wrap_key(password)
            return self.dek

        elif isinstance(kek, KEK) and isinstance(password, bytes):
            unwrapped_kek = kek.unwrap_key(password)
            if isinstance(unwrapped_kek, type(None)):
                return b"FAILED"

            if isinstance(self.result_wrapped_nonce, str):
                result_wrapped_nonce = (self.result_wrapped_nonce.encode()).replace(b"b'", b'')
                result_wrapped_nonce = result_wrapped_nonce[:-1]
                result_wrapped_nonce = result_wrapped_nonce + b'=' * (len(result_wrapped_nonce) % 4)
                self.crypto.nonce = b64decode(result_wrapped_nonce)

            elif isinstance(self.result_wrapped_nonce, bytes):
                self.crypto.nonce = b64decode(self.result_wrapped_nonce)

            if (not isinstance(self.result_wrappedDek, bytes)):
                result_wrappedDek = (self.result_wrappedDek.encode()).replace(b"b'", b'')
                result_wrappedDek = result_wrappedDek[:-1]
                wrapper = result_wrappedDek + b'=' * (len(result_wrappedDek) % 4)

            else:
                result_wrappedDek = self.result_wrappedDek.replace(b"b'", b'')
                result_wrappedDek = result_wrappedDek
                wrapper = result_wrappedDek + b'=' * (len(result_wrappedDek) % 4)

            cryptoObj = CryptoTools()
            self.dek = self.crypto.AesDecryptEAX(b64decode(wrapper), cryptoObj.Sha256(unwrapped_kek))
            kek.wrap_key(password)

            return self.dek

        else:
            try:
                if not isinstance(password, bytes):
                    password = password.encode()
                else:
                    password = password

                kek.unwrap_key(password)
                self.crypto.nonce = b64decode(self.result_wrapped_nonce)
                self.dek = self.crypto.AesDecryptEAX(b64decode(self.result_wrappedDek), self.crypto.Sha256(kek.kek))

                kek.wrap_key(password)
                return self.dek
            except:
                print('someone has attempted to spoof the KEK2 (key encryption key)')


'''
function to DeriveKek_default from an arbitrary password
'''


def DeriveKek_default(password):
    crypto = CryptoTools()
    if len(crypto.Sha256(password.encode())) != LENGTH_OF_KEK:
        print('ERROR> NOT ENOUGH BYTES IN PASSWORD FOR DEK, NEED 32')
    if isinstance(password, str):
        somekek = crypto.Sha256(bytes(password.encode()))
        somekek = crypto.AesEncryptEAX(password.encode(), somekek)
        k = KEK(result_wrapped_kek=b64encode(somekek))
        k.save()
        return k

    elif isinstance(password, bytes):
        somekek = crypto.Sha256(bytes(password.encode()))
        somekek = crypto.AesEncryptEAX(password.encode(), somekek)
        k = KEK(result_wrapped_kek=b64encode(somekek), result_wrapped_nonce=crypto.nonce)
        k.save()
        return k

    else:
        print("ERROR>UNABLE TO GENERATE WRAPPED KEK, USE A CORRECT KEY FORMAT FOR WRAPPING")


'''
NeutronCore is a models.Model type class that allow for KEKs to be generated through a kek generator, time_generated, and of course the kek object
this is the model for when you need access to multiple KEKS for a single user

USE CASE: is old data relies on older KEKs but that older KEK is still active
but the user happened to change their password which would entail creating a new password and from that time the DEK chain would change to the newly
created KEK wrapped using the newly changed password.
'''


class NeutronCore(models.Model):
    kek = models.ForeignKey(
        get_user_model(), related_name='KEK',
        on_delete=models.CASCADE,
        default=1)

    kekgenerator = models.ManyToManyField(KEK, related_name='KEK')

    time_generated = models.DateTimeField('date star collapsed', auto_now_add=True)

    objects = KeyMold()

    class Meta:
        verbose_name = 'neutron core'
        ordering = ['-time_generated']
        get_latest_by = 'time_generated'

    def DeriveKek(self, password):
        crypto = CryptoTools()
        try:
            if len(crypto.Sha256(password.encode())) != LENGTH_OF_KEK:
                print('ERROR> NOT ENOUGH BYTES IN PASSWORD FOR DEK, NEED 32')
        except AttributeError as e:
            print(f"Warning> {e}")
            if len(crypto.Sha256(password)) != LENGTH_OF_KEK:
                print('ERROR> NOT ENOUGH BYTES IN PASSWORD FOR DEK, NEED 32')
        if isinstance(password, str):
            somekek = crypto.Sha256(bytes(password.encode()))
            somekek = crypto.AesEncryptEAX(password.encode(), somekek)
            k = KEK(result_wrapped_kek=b64encode(somekek), result_wrapped_nonce=b64encode(crypto.nonce))
            k.save()
            return k

        elif isinstance(password, bytes):
            somekek = crypto.Sha256(password)
            somekek = crypto.AesEncryptEAX(password, somekek)
            k = KEK(result_wrapped_kek=b64encode(somekek), result_wrapped_nonce=b64encode(crypto.nonce))
            k.save()
            return k

        else:
            print("ERROR>UNABLE TO GENERATE WRAPPED KEK, USE A CORRECT KEY FORMAT FOR WRAPPING")


def DeriveDek_from_Kek(kek: KEK, password: bytes):
    crypto = CryptoTools()

    kekForDek = kek
    if isinstance(kekForDek, KEK):
        if password is not None and isinstance(password, bytes):
            # Generate DEK based off this formula sha256(256 bit SALT + KEK)
            SALT = crypto.RandomNumber(32)

            crypto.nonce = b64decode(kekForDek.result_wrapped_nonce)
            decrypto_kek = crypto.AesDecryptEAX(
                b64decode(kekForDek.result_wrapped_kek),
                crypto.Sha256(password))
            DerivedDek = crypto.Sha256(bytes(SALT) + decrypto_kek)

            crypto.nonce = b64decode(kekForDek.result_wrapped_nonce)

            # dekgenerator = DerivedDek
            dek = DerivedDek
            dek = DEK.wrap_key_static(kekForDek, password, dek)
            newDek = DEK(result_wrappedDek=b64encode(dek), result_SALT=SALT,
                         result_wrapped_nonce=b64encode(crypto.nonce))
            newDek.save()
            newDek.kek_to_retrieve.add(kekForDek)
            newDek.save()
            return newDek


def DeriveDek_default(password):
    crypto = CryptoTools()

    kekForDek = NeutronCore(get_user_model()).DeriveKek(password)
    if isinstance(kekForDek, KEK):
        if password != None and isinstance(password, str):
            # Generate DEK based off this formula sha256(256 bit SALT + KEK)
            self.SALT = crypto.RandomNumber(32)

            crypto.nonce = b64decode(kekForDek.result_wrapped_nonce)
            DerivedDek = crypto.Sha256(bytes(kekForDek.result_SALT) + crypto.AesDecryptEAX(
                bytes(b64decode(str(kekForDek.result_wrapped_kek).encode())),
                crypto.Sha256(bytes(password.encode()))))
            dekgenerator = DerivedDek
            dek = DerivedDek
            dek = DEK.wrap_key(dek, password)
            newDek = DEK(result_wrappedDek=b64encode(dek), result_SALT=kekForDek.result_SALT,
                         kek_to_retrieve=kekForDek, result_wrapped_nonce=b64encode(crypto.nonce))
            newDek.save()
            return newDek


'''
NeutronMatterCollector is for generating a Data Encryption Key [DEK]
no inputs
'''


class NeutronMatterCollector(models.Model):
    dekgenerator = models.ManyToManyField(DEK,
                                          related_name='kek_for_dek_generator')  # length of 32 bytes (256bits) in base64 is 44, but will need to include an = ending and null so extending to 45.

    try:
        kekForDek = models.ForeignKey(
            KEK, related_name='KEK_obj',
            on_delete=models.CASCADE, default=1)
        dek = models.ForeignKey(
            DEK, related_name='DEK_obj',
            on_delete=models.CASCADE,
            default=1)
    except:
        try:
            print("unable to locate KEK for username creating new one, this could be due to a new user")
            kekForDek = models.ForeignKey(KEK, related_name='KEK_obj',
                                          on_delete=models.CASCADE, default=1)
            dek = models.ForeignKey(DEK, related_name='DEK_obj', on_delete=models.CASCADE, default=1)
            print("successfully made a KEK and DEK")

        except:
            print("unable to create KEK")

    time_generated = models.DateTimeField('date integrated', auto_now_add=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    objects = QuasiPlasma()

    class Meta:
        verbose_name = 'neutron matter collector'
        ordering = ['-time_generated']
        get_latest_by = 'time_generated'

    def DeriveDek(self, password):
        crypto = CryptoTools()
        # Ensure this NeutronMatterCollector is saved before using M2M fields
        if self.pk is None:
            self.save()
        if isinstance(NeutronMatterCollector.kekForDek, KEK):
            if password != None and isinstance(password, str):
                # Generate DEK based off this formula sha256(256 bit SALT + KEK)
                self.SALT = crypto.RandomNumber(32)
                crypto.nonce = b64decode(NeutronMatterCollector.kekForDek.result_wrapped_nonce)
                DerivedDek = crypto.Sha256(bytes(self.SALT) + crypto.AesDecryptEAX(
                    bytes(b64decode(str(self.kekForDek.result_wrapped_kek).encode())),
                    crypto.Sha256(bytes(password.encode()))))
                self.dekgenerator = DerivedDek
                dek = DerivedDek
                dek = DEK.wrap_key(dek, password)
                newDek = DEK(result_wrappedDek=b64encode(dek), result_SALT=b64encode(self.SALT),
                             kek_to_retrieve=self.dekgenerator)
                newDek.save()
                return newDek

        else:
            self.kekForDek = NeutronCore(get_user_model()).DeriveKek(password)
            if isinstance(self.kekForDek, KEK):
                if password != None and isinstance(password, str):
                    # Generate DEK based off this formula sha256(256 bit SALT + KEK)
                    self.SALT = crypto.RandomNumber(32)
                    crypto.nonce = b64decode(self.kekForDek.result_wrapped_nonce)
                    DerivedDek = crypto.Sha256(
                        bytes(self.SALT) + crypto.AesDecryptEAX(b64decode(self.kekForDek.result_wrapped_kek),
                                                                crypto.Sha256(bytes(password.encode()))))

                    dek = DerivedDek
                    dek = crypto.AesEncryptEAX(dek, crypto.Sha256(
                        crypto.AesDecryptEAX(b64decode(self.kekForDek.result_wrapped_kek),
                                             crypto.Sha256(bytes(password.encode())))))
                    newDek = DEK(result_wrappedDek=b64encode(dek), result_SALT=b64encode(self.SALT),
                                 result_wrapped_nonce=b64encode(crypto.nonce))
                    newDek.save()
                    self.dekgenerator.set([newDek])
                    self.save()
                    return newDek


class KryptonianSpeak:

    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True
        '''
        db_list = ('default', 'superHeros', 'icePick', 'neutronStarMatter', 'neutronStarMold')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None
        '''

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True


"""
Key Manager for AES keys and RSA keys and ECC keys
"""


# models.py
class AESKey(models.Model):
    key = models.BinaryField()
    salt = models.BinaryField()

    @classmethod
    def generate_key(cls, password):
        salt = os.urandom(32)  # Use a 32-byte salt for AES-256
        key = cls.derive_key(password, salt)

        # Store the key and salt securely (e.g., using an HSM or encrypted storage)
        aes_key = cls.objects.create(key=key, salt=salt)
        return aes_key

    def encrypt_data(self, plaintext):
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(self.key[:16]), backend=default_backend())
        encryptor = cipher.encryptor()

        # Apply PKCS7 padding
        padder = padding.PKCS7(128).padder()
        plaintext_padded = padder.update(plaintext) + padder.finalize()

        ciphertext = encryptor.update(plaintext_padded) + encryptor.finalize()
        return ciphertext

    def decrypt_data(self, ciphertext):
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(self.key[:16]), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt and then remove PKCS7 padding
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(decrypted_data) + unpadder.finalize()
        return plaintext

    @staticmethod
    def derive_key(password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256 requires a 256-bit key
            salt=salt,
            iterations=100000,  # Adjust as needed
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key


# models.py


class RSAKey(models.Model):
    private_key = models.BinaryField()  # need to wrap appropriately
    public_key = models.BinaryField()  # need to wrap appropriately

    wrapped_private_key = models.BinaryField()
    wrapped_public_key = models.BinaryField()
    keys_kek = KEK()
    private_key_dek = DEK()
    public_key_dek = DEK()

    crypto: CryptoTools = CryptoTools()

    @classmethod
    def generate_key_pair(cls, password):
        """
        generates and returns the wrapped public and private keys of RSA that can be decrypted
        with the Password and KEK combination
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        key_encryption_key = DeriveKek_default(password)
        privy_dek = DeriveDek_from_Kek(key_encryption_key, password)
        pub_dek = DeriveDek_from_Kek(key_encryption_key, password)

        wrapped_priv_bytes = cls.crypto.AesEncryptEAX(private_key_bytes, privy_dek.dek)
        wrapped_pub_bytes = cls.crypto.AesEncryptEAX(public_key_bytes, pub_dek.dek)

        rsa_key_pair = cls.objects.create(private_key=wrapped_priv_bytes,
                                          public_key=wrapped_pub_bytes,
                                          keys_kek=key_encryption_key,
                                          wrapped_public_key=wrapped_pub_bytes,
                                          wrapped_private_key=wrapped_priv_bytes,
                                          private_key_dek=privy_dek,
                                          public_key_dek=pub_dek,
                                          )
        privy_dek.wrap_key(key_encryption_key, password)
        pub_dek.wrap_key(key_encryption_key, password)
        key_encryption_key.wrap_key(password)
        secure_erase_bytes(private_key_bytes)
        secure_erase_bytes(public_key_bytes)

        cls.save()
        return rsa_key_pair

    def encrypt_data(self, plaintext):
        public_key = serialization.load_pem_public_key(
            self.public_key,
            backend=default_backend()
        )

        ciphertext = public_key.encrypt(
            plaintext.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return ciphertext

    def decrypt_data(self, ciphertext):
        private_key = serialization.load_pem_private_key(
            self.private_key,
            password=None,
            backend=default_backend()
        )

        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return plaintext.decode()


class UserKeyPair(models.Model):
    """
    Links an RSA-4096 key pair to a user.
    The public key is stored as cleartext PEM (it is public by definition).
    The private key is encrypted with AES-256-EAX via the user's KEK/DEK chain.
    """
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='keypair',
    )
    public_key_pem = models.TextField(
        help_text='RSA-4096 public key in PEM format (cleartext)',
    )
    encrypted_private_key = models.BinaryField(
        help_text='RSA-4096 private key encrypted with AES-256-EAX',
    )
    private_key_nonce = models.CharField(
        max_length=128,
        help_text='Base64-encoded AES-EAX nonce for private key encryption',
    )
    kek = models.ForeignKey(
        KEK,
        on_delete=models.PROTECT,
        related_name='user_keypairs',
    )
    dek = models.ForeignKey(
        DEK,
        on_delete=models.PROTECT,
        related_name='user_keypairs',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'user key pair'
        verbose_name_plural = 'user key pairs'

    def __str__(self):
        return 'KeyPair for {}'.format(self.user.email)

    @classmethod
    def generate_for_user(cls, user, password):
        """
        Generate an RSA-4096 key pair for a user.
        The private key is encrypted under a fresh KEK/DEK derived from
        the user's password. The public key is stored as cleartext PEM.

        Key derivation:
          raw_kek = SHA256(password)            — 32-byte wrapping key
          wrapped_kek = AES-EAX(password, raw_kek)  stored in KEK row
          salt = random 32 bytes
          raw_dek = SHA256(salt + raw_kek)      — 32-byte data key
          wrapped_dek = AES-EAX(raw_dek, raw_kek)  stored in DEK row

        Args:
            user: The User model instance.
            password: bytes or str — the user's raw password.

        Returns:
            UserKeyPair instance (saved to DB).
        """
        from Crypto.PublicKey import RSA as RSAGen

        # Ensure password is bytes
        if isinstance(password, str):
            password = password.encode()

        # Generate RSA-4096 key pair
        rsa_key = RSAGen.generate(4096)
        private_key_pem = rsa_key.export_key(format='PEM')
        public_key_pem = rsa_key.publickey().export_key(format='PEM')

        # --- Derive KEK ---
        # raw_kek is always 32 bytes (SHA-256 digest)
        kek_crypto = CryptoTools()
        raw_kek = kek_crypto.Sha256(password)                          # 32 bytes
        wrapped_kek_bytes = kek_crypto.AesEncryptEAX(password, raw_kek)
        kek = KEK(
            result_wrapped_kek=b64encode(wrapped_kek_bytes),
            result_wrapped_nonce=b64encode(kek_crypto.nonce),
        )
        kek.save()

        # --- Derive DEK from KEK ---
        dek_crypto = CryptoTools()
        salt = dek_crypto.RandomNumber(32)
        raw_dek = dek_crypto.Sha256(bytes(salt) + raw_kek)             # 32 bytes
        # Use the kek nonce for consistency with how unwrap_key works later
        dek_crypto.nonce = kek_crypto.nonce
        wrapped_dek_bytes = dek_crypto.AesEncryptEAX(raw_dek, raw_kek)
        dek = DEK(
            result_wrappedDek=b64encode(wrapped_dek_bytes),
            result_SALT=salt,
            result_wrapped_nonce=b64encode(dek_crypto.nonce),
        )
        dek.save()
        dek.kek_to_retrieve.add(kek)
        dek.save()

        # --- Encrypt the private key PEM with AES-EAX using raw_dek ---
        enc_crypto = CryptoTools()
        encrypted_priv = enc_crypto.AesEncryptEAX(private_key_pem, enc_crypto.Sha256(raw_dek))
        nonce_b64 = b64encode(enc_crypto.nonce).decode()

        # Securely erase raw key material before saving
        secure_erase_bytes(raw_kek)
        secure_erase_bytes(raw_dek)
        secure_erase_bytes(bytearray(private_key_pem))

        keypair = cls.objects.create(
            user=user,
            public_key_pem=public_key_pem.decode(),
            encrypted_private_key=encrypted_priv,
            private_key_nonce=nonce_b64,
            kek=kek,
            dek=dek,
        )
        return keypair

    def get_private_key(self, password):
        """
        Decrypt and return the raw private key PEM bytes.
        CALLER IS RESPONSIBLE for calling secure_erase_bytes() on the result.

        Uses the same derivation path as generate_for_user:
          raw_kek = SHA256(password)
          raw_dek = AES-EAX-decrypt(wrapped_dek, raw_kek) using stored nonce

        Args:
            password: bytes or str — the user's raw password.

        Returns:
            bytes — the decrypted private key in PEM format.
        """
        if isinstance(password, str):
            password = password.encode()

        # Re-derive raw_kek from password (same formula as generate_for_user)
        kek_crypto = CryptoTools()
        raw_kek = kek_crypto.Sha256(password)                          # 32 bytes

        # Unwrap DEK using raw_kek and stored nonce
        dek_crypto = CryptoTools()
        dek_nonce_raw = self.dek.result_wrapped_nonce
        if isinstance(dek_nonce_raw, str):
            dek_nonce_b = dek_nonce_raw.encode().replace(b"b'", b'').rstrip(b"'")
            dek_nonce_b = dek_nonce_b + b'=' * (len(dek_nonce_b) % 4)
        else:
            dek_nonce_b = dek_nonce_raw
        dek_crypto.nonce = b64decode(dek_nonce_b)

        dek_wrapped_raw = self.dek.result_wrappedDek
        if isinstance(dek_wrapped_raw, str):
            dek_wrapped_b = dek_wrapped_raw.encode().replace(b"b'", b'').rstrip(b"'")
            dek_wrapped_b = dek_wrapped_b + b'=' * (len(dek_wrapped_b) % 4)
        else:
            dek_wrapped_b = dek_wrapped_raw
        raw_dek = dek_crypto.AesDecryptEAX(b64decode(dek_wrapped_b), raw_kek)

        if raw_dek is None:
            secure_erase_bytes(raw_kek)
            raise ValueError('Failed to unwrap DEK — wrong password or corrupted key')

        # Decrypt private key using stored nonce
        enc_crypto = CryptoTools()
        enc_crypto.nonce = b64decode(self.private_key_nonce)
        private_key_pem = enc_crypto.AesDecryptEAX(
            bytes(self.encrypted_private_key),
            enc_crypto.Sha256(raw_dek),
        )

        # Erase raw key material
        secure_erase_bytes(raw_kek)
        secure_erase_bytes(raw_dek)

        return private_key_pem

    def get_public_key(self):
        """
        Return the public key PEM bytes (cleartext, no decryption needed).
        """
        return self.public_key_pem.encode()


def secure_erase_bytes(bytes_data) -> bytes:
    bytes_data = bytearray(bytes_data)
    bytes_data = secure_erase(bytes_data)
    print(bytes_data)
    return bytes_data


def secure_erase(byte_data) -> bytes:
    """
    Securely erases the provided bytearray by filling it with random values.
    """
    byte_length = len(byte_data)

    # Generate random bytes using secrets.token_bytes
    random_bytes = secrets.token_bytes(byte_length)

    # Overwrite the original bytearray with random bytes
    for i in range(byte_length):
        byte_data[i] = random_bytes[i]

    # now set them to zero to ensure they key is no longer there.
    for i in range(byte_length):
        byte_data[i] = 0
    print(byte_data)
    return bytes(byte_data)

# Example usage of secure_erase:
# data_to_erase = bytearray(b"Sensitive Data")
# secure_erase(data_to_erase)
# print("Erased Data:", data_to_erase)
