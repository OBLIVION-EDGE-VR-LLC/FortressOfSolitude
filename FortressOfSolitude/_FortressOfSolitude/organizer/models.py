"""
DBA 1337_TECH, AUSTIN TEXAS © DEC 2021
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

import os
from base64 import (b64encode, b64decode)
from datetime import datetime
from ctypes import Union

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from django.utils import timezone

import _FortressOfSolitude.settings as settings
from _FortressOfSolitude.NeutrinoKey.cryptoutils import CryptoTools
from _FortressOfSolitude.NeutrinoKey.models import secure_erase_bytes, secure_erase
from _FortressOfSolitude.NeutrinoKey.models import DEK, KEK, NeutronMatterCollector, NeutronCore, DeriveDek_default, \
    DeriveDek_from_Kek

from ckeditor.fields import RichTextField

# Create your models here.

# Constants
musicFS = FileSystemStorage(location=settings.STATIC_ROOT + '/media/music/')
photoFS = FileSystemStorage(location=settings.STATIC_ROOT + '/media/photos/')
videoFS = FileSystemStorage(location=settings.STATIC_ROOT + '/media/video/')
otherFS = FileSystemStorage(location=settings.STATIC_ROOT + '/media/otherfiles/')


# End of Constants


class TaskingManager(models.Manager):
    """
    Tasking Manager is a models.Manager class extension that is used to retrieving the correct Tasking model type
    no inputs
    """

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


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
        model_data: Union[ImageFile, MusicFile, MiscFile] = kwargs.pop('image_file', False)

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
        data.data_kek = data_kek
        data.data_dek = data_dek
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
            if data_dek:
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
                if isinstance(secureNote, SecureNotePublic):
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


class Tag(models.Model):
    """
    Tag is a generic "model" class that contains two charfields:name and slug, the name is for the title of the tag
    and the slug is for the unique url no inputs
    """
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True, help_text='A label for URL config.')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name.title()

    def get_absolute_url(self):
        return reverse('organizer_tag_detail', kwargs={'slug': self.slug})


class Tasking(models.Model):
    """
    Tasking is a model class that contains a name slug, asignee, project_codename, description, and assigned_date It
    is used to keep track of your work no inputs
    """
    name = models.CharField(max_length=32, unique=True, db_index=True)
    slug = models.SlugField(max_length=32, unique=True, db_index=True)
    asignee = models.CharField(max_length=16, db_index=True)
    project_codename = models.CharField(default='SandStorm', max_length=32, db_index=True)
    description = models.TextField()
    assigned_date = models.DateTimeField('date assigned', unique=True,
                                         auto_now_add=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    is_complete = models.BooleanField(default=False)

    objects = TaskingManager()

    class Meta:
        ordering = ['name']
        get_latest_by = 'assigned_date'

    def __str__(self):
        return self.name.title()

    def get_absolute_url(self):
        return reverse('organizer_tasking_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('organizer_tasking_update', kwargs={'slug': self.slug})

    def natural_key(self):
        return (self.slug,)


class Startup(models.Model):
    """
    Startup is  a model class that contains a name, slug, description, founded_date, contact, website, and associated
    tags. This is used for a startup company no inputs
    """
    name = models.CharField(max_length=32, db_index=True)
    slug = models.SlugField(max_length=32, unique=True, help_text='A label for URL config.')
    description = models.TextField()
    founded_date = models.DateField('date founded')
    contact = models.EmailField()
    website = models.URLField(max_length=64)
    tags = models.ManyToManyField(Tag)

    def __str(self):
        return self.name

    class Meta:
        ordering = ['name']
        get_latest_by = 'founded_date'

    def get_absolute_url(self):
        return reverse('organizer_startup_detail', kwargs={'slug', self.slug})


class NewsLink(models.Model):
    """
    NewsLink is a models.Model class that contains a title, pub_date, link, and startup used for publishing articles
    no inputs
    """
    title = models.CharField(max_length=64)
    pub_date = models.DateField('date published')
    link = models.URLField(max_length=64)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}".format(self.startup, self.title)

    class Meta:
        verbose_name = 'news article'
        ordering = ['-pub_date']
        get_latest_by = 'pub_date'


class MusicFile(models.Model):
    """
    MusicFile is a models.Model that contains image_file, data_dek, data_kek, and result_nonce_file: used for
    encrypting music files and organizing into the music folder no inputs
    """
    image_file = models.FileField(storage=musicFS, default=None)
    data_dek = models.ForeignKey(DEK, default=1, on_delete=models.CASCADE)
    data_kek = models.ForeignKey(KEK, default=1, on_delete=models.CASCADE)
    result_nonce_file = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))

    objects = Librarian()

    class Meta:
        ordering = ['image_file']

    def __str__(self):
        return str(self.image_file)

    def get_absolute_url(self):
        return reverse('organizer_music_download_pull', kwargs={
            'image_file': self.image_file})  # Need to test if actually works for download or if the function needs to decrypt

    def get_update_url(self):
        return reverse('organizer_upload_create', kwargs={
            'image_file': self.image_file})  # Need to test if actually works for upload or if the function needs to encrypt

    def natural_key(self):
        return (self.image_file,)


class ImageFile(models.Model):
    """
    ImageFile is a models.Model class that contains a image_file, data_dek, data_kek, and result_nonce_file for
    encrypting and organizing common image files common image files will be .png, .tiff, .bmp no inputs
    """
    image_file = models.FileField(storage=photoFS, default=None)
    data_dek = models.ManyToManyField(DEK, default=1)
    data_kek = models.ManyToManyField(KEK, default=1)
    result_nonce_file = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))

    objects = Librarian()

    class Meta:
        ordering = ['-image_file']

    def __str__(self):
        return str(self.image_file)

    def get_absolute_url(self, **kwargs):
        if str(self.image_file) != '':
            print(dir(self))
            return reverse('organizer_download_pull', kwargs={
                'image_file': self.image_file})

    def get_update_url(self):
        if str(self.image_file) != '':
            return reverse('organizer_upload_create', kwargs={
                'image_file': self.image_file})

    def natural_key(self):
        return (self.image_file,)

    natural_key.dependencies = [
        # 'organizer.startup',
        'NeutrinoKey.DEK',
        'NeutrinoKey.KEK',
    ]


class VideoFile(models.Model):
    """
    VideoFile is a models.Model type class that contains image_file, data_dek, data_kek, and result_nonce_file for
    encrypting and organizing video files common video formats will be .mpg, .mp4, .avi, .mkv no inputs
    """
    image_file = models.FileField(storage=videoFS, default=None)
    data_dek = models.ManyToManyField(DEK, default=1)
    data_kek = models.ManyToManyField(KEK, default=1)
    result_nonce_file = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))

    objects = Librarian()

    class Meta:
        ordering = ['-image_file']

    def __str__(self):
        return str(self.image_file)

    def get_absolute_url(self):
        return reverse('organizer_video_download_pull', kwargs={'image_file': str(
            self.image_file)})  # Need to test if actually works for download or if the function needs to decrypt

    def get_update_url(self):
        return reverse('organizer_upload_create', kwargs={
            'image_file': self.image_file})

    def natural_key(self):
        return (self.image_file,)

    def natural_key(self):
        return (self.image_file,)


class MiscFile(models.Model):
    """
    MiscFile is a models.Model type class extension that includes an image_file, data_dek, data_kek,
    and result_nonce_file that is used to encrypt and organize extension file types that haven't been listed in
    previous classes such as ImageFile, MusicFile, and VideoFile no inputs
    """
    image_file = models.FileField(storage=otherFS, default=None)
    data_dek = models.ForeignKey(DEK, default=1, on_delete=models.CASCADE)
    data_kek = models.ForeignKey(KEK, default=1, on_delete=models.CASCADE)
    result_nonce_file = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))

    objects = Librarian()

    class Meta:
        ordering = ['-image_file']

    def __str__(self):
        return str(self.image_file)

    def get_absolute_url(self):
        return reverse('organizer_misc_download_pull', kwargs={
            'image_file': self.image_file})

    def get_update_url(self):
        return reverse('organizer_upload_create', kwargs={
            'image_file': self.image_file})

    def natural_key(self):
        return (self.image_file,)


class SecureNote(models.Model):
    """
    Used as sort of a Base class for a Securing Arbitrary Text which is used as an example in the
    _FortressOfSolitude.Blog.models.SecureDataAtRestPost which inherits this class to more or less
    simply be a little 'organized' as to what is all required to secure a Note.  At the moment you need
    to have a data_dek and data_kek already stored in the database in order to begin generating
    it doesn't actually select the data_kek and data_dek, there is a form slot for it but no matter
    what it will randomly generate one in case there is someone trying to reuse keys.  I saw this as a
    potential security flaw if you could use the same key for a different file.
    """
    slug = models.SlugField(max_length=32, unique=True, db_index=True, help_text='A label for URL config.')
    title = models.CharField(max_length=64, default='Bruh, Change the Title')
    pub_date = models.DateTimeField('date published', auto_now_add=timezone.now())
    secure_text = models.TextField(default="Please add Note Text")
    data_dek = models.ManyToManyField(DEK, default=1, related_name='data_dek')
    data_kek = models.ManyToManyField(KEK, default=1, related_name='data_kek')
    result_nonce_text = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))

    # objects = Librarian()

    class Meta:
        abstract = True
        ordering = ['-secure_text']

    def __str__(self):
        return "{} on {}".format(
            self.title,
            self.pub_date)

    def get_absolute_url(self):
        return reverse('blog_securepost_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('blog_securepost_update', kwargs={'slug': self.slug})

    def natural_key(self):
        return (self.slug,)


class SecureNotePublic(models.Model):
    """
    Used as sort of a Base class for a Securing Arbitrary Text to be viewed as a Public Post which is used as an example in the
    _FortressOfSolitude.Blog.models.SecureDataAtRestPost which inherits this class to more or less
    simply be a little 'organized' as to what is all required to secure a Note.  At the moment you need
    to have a data_dek and data_kek already stored in the database in order to begin generating
    it doesn't actually select the data_kek and data_dek, there is a form slot for it but no matter
    what it will randomly generate one in case there is someone trying to reuse keys.  I saw this as a
    potential security flaw if you could use the same key for a different file.
    """
    slug = models.SlugField(max_length=32, unique=True, db_index=True, help_text='A label for URL config.')
    title = models.CharField(max_length=64, default='Bruh, Change the Title')
    pub_date = models.DateTimeField('date published', auto_now_add=timezone.now())
    secure_text = RichTextField(blank=True, null=True)  # models.TextField(default="Please add Note Text")
    data_dek = models.ManyToManyField(DEK, default=1, related_name='data_dek_public')
    data_kek = models.ManyToManyField(KEK, default=1, related_name='data_kek_public')
    result_nonce_text = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))

    # objects = Librarian()

    class Meta:
        abstract = True
        ordering = ['-secure_text']

    def __str__(self):
        return "{} on {}".format(
            self.title,
            self.pub_date)

    def get_absolute_url(self):
        return reverse('blog_public_securepost_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('blog_public_securepost_update', kwargs={'slug': self.slug})

    def natural_key(self):
        return (self.slug,)
