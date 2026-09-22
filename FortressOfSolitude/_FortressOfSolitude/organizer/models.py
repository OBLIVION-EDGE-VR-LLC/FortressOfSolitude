"""
DBA 1337_TECH, AUSTIN TEXAS © DEC 2021
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

import os
from base64 import (b64encode, b64decode)
from datetime import datetime
from ctypes import Union

from django.contrib.auth import get_user_model
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

from _FortressOfSolitude.core.managers import Librarian, Gor_El
from _FortressOfSolitude.core.models import SecureNotePublic

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
    folder = models.ForeignKey(
        'UserFolder', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_files',
    )

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
    folder = models.ForeignKey(
        'UserFolder', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_files',
    )

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
    folder = models.ForeignKey(
        'UserFolder', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_files',
    )

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
    folder = models.ForeignKey(
        'UserFolder', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_files',
    )

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


class UserFolder(models.Model):
    """
    Encrypted folder hierarchy for users. Each folder has its own DEK
    (per-scope encryption), all sharing the user's root KEK.
    Enables folder-level sharing via proxy re-encryption in Sub-project 3.
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='children',
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='folders',
    )
    kek = models.ForeignKey(
        KEK, on_delete=models.PROTECT,
        related_name='folders',
    )
    dek = models.ForeignKey(
        DEK, on_delete=models.PROTECT,
        related_name='folders',
    )
    dek_nonce = models.CharField(
        max_length=128,
        help_text='Base64-encoded nonce for this folder DEK',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('owner', 'parent', 'name')]
        ordering = ['name']

    def __str__(self):
        return f'{self.owner.email}:/{self.get_path()}'

    def get_path(self):
        """Return the full path string like 'root/projects/alpha'."""
        parts = [f.name for f in self.get_breadcrumbs()]
        return '/'.join(parts)

    def get_children(self):
        """Return direct child folders."""
        return UserFolder.objects.filter(parent=self)

    def get_breadcrumbs(self):
        """Return list of folders from root to self."""
        breadcrumbs = []
        current = self
        while current is not None:
            breadcrumbs.append(current)
            current = current.parent
        breadcrumbs.reverse()
        return breadcrumbs

    @classmethod
    def create_root_for_user(cls, user, password):
        """
        Create the root folder and default subfolders for a user.
        If root already exists, return it without creating duplicates.
        password must be bytes.
        """
        existing = cls.objects.filter(owner=user, parent=None, name='root').first()
        if existing:
            return existing

        if isinstance(password, str):
            password = password.encode()

        crypto = CryptoTools()

        # Derive a KEK for this user's folder tree
        nc, _ = NeutronCore.objects.get_or_create(kek=user)
        kek = nc.DeriveKek(password)

        # Derive root DEK
        raw_kek = crypto.Sha256(password)
        salt = crypto.RandomNumber(32)
        raw_dek = crypto.Sha256(salt + raw_kek)

        crypto.nonce = None
        wrapped_dek = crypto.AesEncryptEAX(raw_dek, raw_kek)
        dek_nonce_b64 = b64encode(crypto.nonce).decode()

        dek = DEK(
            result_wrappedDek=b64encode(wrapped_dek).decode(),
            result_SALT=b64encode(salt).decode(),
            result_wrapped_nonce=b64encode(crypto.nonce).decode(),
        )
        dek.save()
        dek.kek_to_retrieve.add(kek)

        secure_erase_bytes(raw_dek)
        secure_erase_bytes(raw_kek)

        root = cls.objects.create(
            name='root',
            slug='root',
            parent=None,
            owner=user,
            kek=kek,
            dek=dek,
            dek_nonce=dek_nonce_b64,
        )

        # Create default subfolders, each with its own DEK
        default_folders = ['journal', 'projects', 'music', 'files', 'inbox']
        for folder_name in default_folders:
            cls.create_subfolder(
                parent=root,
                name=folder_name,
                password=password,
            )

        return root

    @classmethod
    def create_subfolder(cls, parent, name, password):
        """
        Create a subfolder under parent with its own DEK,
        sharing the parent's KEK.
        """
        from django.utils.text import slugify

        if isinstance(password, str):
            password = password.encode()

        crypto = CryptoTools()
        raw_kek = crypto.Sha256(password)
        salt = crypto.RandomNumber(32)
        raw_dek = crypto.Sha256(salt + raw_kek)

        crypto.nonce = None
        wrapped_dek = crypto.AesEncryptEAX(raw_dek, raw_kek)
        dek_nonce_b64 = b64encode(crypto.nonce).decode()

        dek = DEK(
            result_wrappedDek=b64encode(wrapped_dek).decode(),
            result_SALT=b64encode(salt).decode(),
            result_wrapped_nonce=b64encode(crypto.nonce).decode(),
        )
        dek.save()
        dek.kek_to_retrieve.add(parent.kek)

        secure_erase_bytes(raw_dek)
        secure_erase_bytes(raw_kek)

        folder = cls.objects.create(
            name=name,
            slug=slugify(name),
            parent=parent,
            owner=parent.owner,
            kek=parent.kek,
            dek=dek,
            dek_nonce=dek_nonce_b64,
        )
        return folder


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


# SecureNotePublic has been moved to _FortressOfSolitude.core.models
# It is re-exported here via: from _FortressOfSolitude.core.models import SecureNotePublic
