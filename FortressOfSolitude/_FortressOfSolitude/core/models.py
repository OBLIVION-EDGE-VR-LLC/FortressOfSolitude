"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.

Bridge module: shared abstract models used by organizer and agora apps.
"""

from base64 import b64encode

from django.db import models
from django.urls import reverse
from django.utils import timezone

from ckeditor.fields import RichTextField
from _FortressOfSolitude.NeutrinoKey.models import DEK, KEK


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
    secure_text = RichTextField(blank=True, null=True)
    data_dek = models.ManyToManyField(DEK, default=1, related_name='data_dek_public')
    data_kek = models.ManyToManyField(KEK, default=1, related_name='data_kek_public')
    result_nonce_text = models.CharField(max_length=128, default=b64encode(int(55).to_bytes(4, 'big')))

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
