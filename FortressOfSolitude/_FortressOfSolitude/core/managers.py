"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.

Bridge module: shared encryption managers used by organizer and agora apps.
"""

import os
from base64 import (b64encode, b64decode)

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.db import models

import _FortressOfSolitude.settings as settings
from _FortressOfSolitude.NeutrinoKey.cryptoutils import CryptoTools
from _FortressOfSolitude.NeutrinoKey.models import (
    secure_erase_bytes, secure_erase,
    DEK, KEK, NeutronMatterCollector, NeutronCore,
    DeriveDek_default, DeriveDek_from_Kek,
)


# Lazy import to avoid circular dependency — SecureNotePublic will be in core.models
def _is_secure_note_public(instance):
    from _FortressOfSolitude.core.models import SecureNotePublic
    return isinstance(instance, SecureNotePublic)


class Librarian(models.Manager):
    """
    Librarian is a models.Manager class extension that includes a NeutronMatterCollector object, NeutronCore object,
    and CryptoTools object. The Librarian is a helper class that does the encrypting used for decompartmentalizing
    the roles of encryption and decryption to be seperated logically by classes. Use _encrypt_data to encrypt then
    store the appropriate model into the "fortressvault" database.  furthermore the Librarian is responsible for
    securing, then organizing data at rest.
    """

    crypt = CryptoTools()

    def get_queryset(self):
        qs = models.QuerySet(self.model)
        if self._db:
            qs = qs.using('default')
        return qs

    def _encrypt_update_Secure_Note(self, password, **kwargs):
        modeldata = kwargs.pop('secure_text', False)

        req = kwargs.pop('request', False)
        post = kwargs.pop('postobj', False)

        data_kek = NeutronCore().DeriveKek(password)
        data_dek = NeutronMatterCollector().DeriveDek(password)
        nonce = data_dek.result_wrapped_nonce
        Librarian.crypt.nonce = b64decode(nonce)
        if not isinstance(password, bytes):
            password = password.encode()
        key = data_dek.unwrap_key(data_kek, password)

        if isinstance(modeldata, str):
            modeldata = modeldata.encode()
        encrypted_data = Librarian.crypt.AesEncryptEAX(modeldata, DEK.crypto.Sha256(key))

        post.secure_text = encrypted_data
        post.save()
        # post.data_dek.remove(post.data_dek.get())
        # post.data_kek.remove(post.data_kek.get())  # change this before deployment
        post.save()
        data_kek.save()
        data_dek.save()
        post.data_dek.add(data_dek)
        post.data_kek.add(data_kek)
        print("SECURED A NOTE: ENCRYPTED Sending off to Save")

        post.save()

        return post

    def _encrypt_Daily_Planet_Note(self, password, **kwargs):
        modeldata = kwargs.pop('secure_text', False)

        req = kwargs.pop('request', False)
        post = kwargs.pop('postobj', False)

        data_kek = NeutronCore().DeriveKek(self.crypt.Sha256(settings.DAILY_PLANET_AES_DEK))
        # data_dek = NeutronMatterCollector().DeriveDek(settings.DAILY_PLANET_AES_DEK)
        # data_dek = DeriveDek_default(settings.DAILY_PLANET_AES_DEK)
        data_dek = DeriveDek_from_Kek(data_kek, self.crypt.Sha256(settings.DAILY_PLANET_AES_DEK))
        nonce = data_kek.result_wrapped_nonce
        Librarian.crypt.nonce = b64decode(nonce)
        if not isinstance(password, bytes):
            password = password.encode()
        key = data_kek.unwrap_key(self.crypt.Sha256(settings.DAILY_PLANET_AES_DEK))

        if isinstance(modeldata, str):
            modeldata = modeldata.encode()
        encrypted_data = Librarian.crypt.AesEncryptEAX(modeldata, DEK.crypto.Sha256(key))

        post.secure_text = encrypted_data
        post.save()
        data_kek.save()
        data_dek.save()
        post.data_kek.add(data_kek)
        post.data_dek.add(data_dek)

        print("SECURED A NOTE: ENCRYPTED Sending off to Save")

        post.save()

        return post

    def _encrypt_Secure_Note(
            self, password, **kwargs):
        modeldata = kwargs.pop('secure_text', False)

        req = kwargs.pop('request', False)
        post = kwargs.pop('postobj', False)

        data_kek = NeutronCore().DeriveKek(password)
        data_dek = NeutronMatterCollector().DeriveDek(password)
        nonce = data_dek.result_wrapped_nonce
        Librarian.crypt.nonce = b64decode(nonce)
        if not isinstance(password, bytes):
            password = password.encode()
        key = data_dek.unwrap_key(data_kek, password)

        if isinstance(modeldata, str):
            modeldata = modeldata.encode()
        encrypted_data = Librarian.crypt.AesEncryptEAX(modeldata, DEK.crypto.Sha256(key))

        post.secure_text = encrypted_data
        post.save()
        data_kek.save()
        data_dek.save()
        post.data_kek.add(data_kek)
        post.data_dek.add(data_dek)

        print("SECURED A NOTE: ENCRYPTED Sending off to Save")

        post.save()

        return post

    def _encrypt_data(
            self, password, **kwargs):
        from _FortressOfSolitude.organizer.models import (
            ImageFile, MusicFile, VideoFile, MiscFile,
            photoFS, musicFS, videoFS, otherFS,
        )
        from ctypes import Union
        model_data = kwargs.pop('image_file', False)

        req = kwargs.pop('request', False)
        modeldata = req.FILES['file_field'].read()
        data_kek = NeutronCore().DeriveKek(password)
        data_dek = NeutronMatterCollector().DeriveDek(password)
        nonce = data_dek.result_wrapped_nonce
        Librarian.crypt.nonce = b64decode(nonce)
        if not isinstance(password, bytes):
            password = password.encode()
        key = data_dek.unwrap_key(data_kek, password)

        encrypted_data = Librarian.crypt.AesEncryptEAX(modeldata, DEK.crypto.Sha256(key))
        file_data = ContentFile(encrypted_data)
        filename = req.FILES['file_field'].name

        data = self.model(
            image_file=file_data,
            **kwargs)
        data.image_file.name = filename
        print(f"data.image_file.name {model_data.image_file.name}")
        data.result_nonce_file = nonce
        data.save()
        data_dek.save()
        data_kek.save()
        data.data_kek.set([data_kek])
        data.data_dek.set([data_dek])
        print("ENCRYPTED AND SAVED DATA")
        data.save()

        # *** THIS IS THE HACKY CODE BELOW, change to STATIC location when able ***
        if isinstance(model_data, ImageFile):
            fd = open('/' + os.path.join(photoFS.base_location, str(data)), 'w+')
            fd.close()
            fd = open('/' + os.path.join(photoFS.base_location, str(data)), 'wb')

        elif isinstance(model_data, MusicFile):
            fd = open('/' + os.path.join(musicFS.base_location, str(data)), 'w+')
            fd.close()
            fd = open('/' + os.path.join(musicFS.base_location, str(data)), 'wb')

        elif isinstance(model_data, VideoFile):
            fd = open('/' + os.path.join(videoFS.base_location, str(data)), 'w+')
            fd.close()
            fd = open('/' + os.path.join(videoFS.base_location, str(data)), 'wb')

        elif isinstance(model_data, MiscFile):
            fd = open('/' + os.path.join(otherFS.base_location, str(data)), 'w+')
            fd.close()
            fd = open('/' + os.path.join(otherFS.base_location, str(data)), 'wb')

        else:
            print("something went horrible and terribly wrong unable to determine where to encrypt data")
            return None

        # *** end of hacky code ***

        # END OF HACKY CODE
        fd.write(encrypted_data)
        fd.close()
        return data


class Gor_El(models.Manager):
    """
    Gor_El is a models.Manager class extension that includes a NeutronMatterCollector object, NeutronCore object,
    and CryptoTools object it is used to retrieve data from the fortressvault database as well as to answer the
    questions of Kal-El or simply decrypts the information stored on the server includes two flavors of decryption
    _decrypt_model and _decrypt_data as of writing only ImageFiles can be correctly decrypted. Furthermore Gor_El is
    responsible for retrieving and then decrypting data at rest while ensuring that the original data remains secured
    at rest.  Thus it acts as an interpretor for kryptonian speak.

    TODO: Correctly Decrypt VideoFile, and MiscFile using the _decrypt_data function
    """
    crypt = CryptoTools()

    def get_queryset(self):
        qs = models.QuerySet(self.model)
        if self._db is not None:
            qs = qs.using('default')
        return qs

    def _decrypt_model(self, image_file, **kwargs):
        from _FortressOfSolitude.organizer.models import photoFS
        newpath = photoFS.base_location + str('decrypted_' + str(image_file))
        encryptedFile = open('/' + photoFS.base_location + str(image_file), 'rb').read()
        self.crypt.nonce = b64decode(image_file.result_nonce_file)
        password = kwargs.pop('password', False)
        keyToFile = image_file.data_dek.unwrap_key(image_file.data_kek, password.encode())
        hash = CryptoTools()
        plaintext = self.crypt.AesDecryptEAX(encryptedFile, hash.Sha256(keyToFile))
        x = ContentFile(plaintext)
        return x

    def _decrypt_text(self, secureNote, request):
        ciphertext = secureNote.secure_text
        data_dek = secureNote.data_dek
        data_kek = secureNote.data_kek
        try:
            if not data_dek.exists():
                return b"Look the data_dek got deleted wise guy"
            data_dek = data_dek.get()
        except MultipleObjectsReturned as e:
            print(e)
            print("looking for the latest obejct now")
            print(dir(data_dek))
            data_dek_list: list[DEK] = data_dek.values_list()
            print(tuple)
            print(f"DATA DEK LIST: {data_dek_list}")
            data_dek = data_dek_list[len(data_dek_list) -1] # assume the most up to date key is the last one
            print(f"we found something ---> {data_dek} <--shouldn't be None")
        # data_kek = data_kek.get()
        # now make sure their in the correct format
        try:
            if isinstance(secureNote.data_dek.get().result_wrapped_nonce, str):
                if _is_secure_note_public(secureNote):
                    request.user = AnonymousUser()
                    raise(Exception, "Look here you need to be Anonymous to read the Anonymous blog post")
                wrapped_nonce = (secureNote.data_dek.get().result_wrapped_nonce.encode()).replace(b"b'", b'')
                wrapped_nonce = wrapped_nonce.replace(b"'", b'')
                wrapped_nonce = wrapped_nonce + b'=' * (len(wrapped_nonce) % 4)
                self.crypt.nonce = b64decode(wrapped_nonce)
            else:
                self.crypt.nonce = b64decode(secureNote.data_dek.get().result_wrapped_nonce)

            if isinstance(secureNote.secure_text, str):
                ciphertext = secureNote.secure_text
                ciphertext = ciphertext.encode('latin1').decode('unicode-escape').encode('latin1')
                ciphertext = ciphertext[2:len(ciphertext) - 1]
            else:
                ciphertext = ciphertext.encode()

            data_dek = secureNote.data_dek.get(id=secureNote.data_dek.get().id)

        except Exception as e:
            print(e)

            # data_dek = DEK()

            if isinstance(secureNote.secure_text, str):
                ciphertext = secureNote.secure_text
                ciphertext = ciphertext.encode('latin1').decode('unicode-escape').encode('latin1')
                ciphertext = ciphertext[2:len(ciphertext) - 1]
            else:
                ciphertext = ciphertext.encode()

            if str(request.user) == "AnonymousUser":
                data_dek: DEK = secureNote.data_dek.get()
                data_kek: KEK = secureNote.data_kek.get()
                # data_kek.crypto.nonce = b64decode(data_kek.result_wrapped_nonce)
                key = data_kek.unwrap_key(CryptoTools().Sha256(settings.DAILY_PLANET_AES_DEK))

                if key is None:
                    return None

                password = settings.DAILY_PLANET_AES_DEK
                nonce = data_kek.result_wrapped_nonce
                # data_dek.nonce = b64decode(nonce)

                if isinstance(nonce, str):
                    result_wrapped_nonce = (nonce.encode()).replace(b"b'", b'')
                    result_wrapped_nonce = result_wrapped_nonce[:-1]
                    result_wrapped_nonce = result_wrapped_nonce + b'=' * (len(result_wrapped_nonce) % 4)
                    data_dek.crypto.nonce = b64decode(result_wrapped_nonce)

                if isinstance(data_dek.result_wrappedDek, str):
                    dek = (data_dek.result_wrappedDek.encode()).replace(b"b'", b'')
                    dek = dek[:-1]
                    dek = dek + b'=' * (len(dek) % 4)
                    # daka_dek.crypt.nonce = b64decode(result_wrapped_nonce)

                data_key = data_dek.crypto.AesDecryptEAX(b64decode(dek), key)

                # dek_key = data_dek.unwrap_key(data_kek, CryptoTools().Sha256(password))
                self.crypt.nonce = b64decode(nonce)
            else:
                password = request.user.password.encode()
            keyToFile = settings.DAILY_PLANET_AES_DEK

        hash = CryptoTools()

        if str(request.user) == "AnonymousUser":
            data_dek.crypto.nonce = b64decode(result_wrapped_nonce)
            plaintext = data_dek.crypto.AesDecryptEAX(ciphertext, CryptoTools().Sha256(key))
        else:
            plaintext = self.crypt.AesDecryptEAX(ciphertext, data_dek)
        print("securely erasing the keyToFile in memory")
        key = secure_erase_bytes(key)
        print("erased keyToFile in memory")
        print(f"key: {key}")
        del key
        return plaintext

    def _decrypt_data(self, password, **kwargs):
        from _FortressOfSolitude.organizer.models import photoFS, musicFS, otherFS
        plaintext = None
        f = kwargs.pop('image_file', False)
        req = kwargs.pop('request', False)
        if str(f.image_file).lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            encryptedFile = open('/' + os.path.join(photoFS.base_location, str(f.image_file.name)), 'rb').read()
            data_kek: KEK = f.data_kek

            data_dek: DEK = f.data_dek

            # We've got the dek and kek attached to the image file so now to do the decryption
            if isinstance(f.result_nonce_file, str):
                wrapped_nonce = (f.result_nonce_file).encode('latin1').decode('unicode-escape').encode('latin1')
                wrapped_nonce = wrapped_nonce[2:-1]
                wrapped_nonce = wrapped_nonce + b'=' * (len(wrapped_nonce) % 4)
                self.crypt.nonce = b64decode(wrapped_nonce)
            else:
                self.crypt.nonce = b64decode(f.data_dek.get().result_nonce_file)

            keyToFile = data_dek.get().unwrap_key(data_kek.get(), password.encode())

            self.crypt.nonce = b64decode(wrapped_nonce)
            plaintext = self.crypt.AesDecryptEAX(encryptedFile, CryptoTools().Sha256(keyToFile))
            return plaintext

        elif str(f.image_file).lower().endswith(('.mp3', '.m4p', '.m4a', '.flac', '.aac')):
            print("DEBUG>PATH:" + str(os.path.join(musicFS.base_location, str(f.image_file.name))))
            encryptedFile = open('/' + os.path.join(musicFS.base_location, str(f.image_file.name)), 'rb').read()
            data_kek: KEK = f.data_kek

            data_dek: DEK = f.data_dek

            # We've got the dek and kek attached to the image file so now to do the decryption
            if isinstance(f.result_nonce_file, str):
                wrapped_nonce = (f.result_nonce_file).encode('latin1').decode('unicode-escape').encode('latin1')
                wrapped_nonce = wrapped_nonce[2:-1]
                wrapped_nonce = wrapped_nonce + b'=' * (len(wrapped_nonce) % 4)
                self.crypt.nonce = b64decode(wrapped_nonce)
            else:
                self.crypt.nonce = b64decode(f.data_dek.result_nonce_file)

            keyToFile = data_dek.unwrap_key(data_kek, password.encode())

            self.crypt.nonce = b64decode(wrapped_nonce)
            plaintext = self.crypt.AesDecryptEAX(encryptedFile, CryptoTools().Sha256(keyToFile))
            print("securely erasing the keyToFile in memory")
            secure_erase_bytes(keyToFile)
            print("erased keyToFile in memory")
            return plaintext

        else:
            print("DEBUG>PATH:" + str(os.path.join(otherFS.base_location, str(f.image_file.name))))
            encryptedFile = open('/' + os.path.join(otherFS.base_location, str(f.image_file.name)), 'rb').read()
            data_kek: KEK = f.data_kek

            data_dek: DEK = f.data_dek

            # We've got the dek and kek attached to the image file so now to do the decryption
            if isinstance(f.result_nonce_file, str):
                wrapped_nonce = (f.result_nonce_file).encode('latin1').decode('unicode-escape').encode('latin1')
                wrapped_nonce = wrapped_nonce[2:-1]
                wrapped_nonce = wrapped_nonce + b'=' * (len(wrapped_nonce) % 4)
                self.crypt.nonce = b64decode(wrapped_nonce)
            else:
                self.crypt.nonce = b64decode(f.data_dek.result_nonce_file)

            keyToFile = data_dek.unwrap_key(data_kek, password.encode())

            self.crypt.nonce = b64decode(wrapped_nonce)
            plaintext = self.crypt.AesDecryptEAX(encryptedFile, CryptoTools().Sha256(keyToFile))
            return plaintext

        return plaintext
