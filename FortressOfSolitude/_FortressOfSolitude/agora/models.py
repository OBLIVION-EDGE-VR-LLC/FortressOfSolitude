"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from _FortressOfSolitude.core.managers import Librarian
from _FortressOfSolitude.core.models import SecureNotePublic
from _FortressOfSolitude.NeutrinoKey.models import DEK, KEK
from _FortressOfSolitude.organizer.models import Tag


handle_validator = RegexValidator(
    regex=r'^[\w-]+$',
    message='Handle may only contain letters, numbers, hyphens, and underscores.',
)


class AgoraProfile(models.Model):
    """
    A user's public identity in The Agora.
    Login is via email, but all forum presence is through the handle.
    """
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='agora_profile',
    )
    handle = models.CharField(
        max_length=64,
        unique=True,
        validators=[handle_validator],
        help_text='Your public name in The Agora (letters, numbers, hyphens, underscores).',
    )
    about_me = models.TextField(max_length=1000, blank=True, default='')
    favorite_movie = models.CharField(max_length=128, blank=True, default='')
    favorite_song = models.CharField(max_length=128, blank=True, default='')
    favorite_artist = models.CharField(max_length=128, blank=True, default='')
    quote = models.TextField(max_length=1000, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'agora profile'
        verbose_name_plural = 'agora profiles'

    def __str__(self):
        return self.handle

    def get_absolute_url(self):
        return reverse('agora_profile_detail', kwargs={'handle': self.handle})


class Category(models.Model):
    """
    A top-level category (market) in The Agora.
    Admin-managed; seeded with four core categories.
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('agora_category_detail', kwargs={'category_slug': self.slug})


class Topic(SecureNotePublic):
    """
    A forum topic in The Agora. Encrypted at rest via the Daily Planet model.
    Content is publicly readable through the interface by any authenticated user.
    """
    author = models.ForeignKey(
        AgoraProfile,
        on_delete=models.CASCADE,
        related_name='topics',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='topics',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='agora_topics',
        blank=True,
    )
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    # Override inherited M2M fields with unique related_names
    data_dek = models.ManyToManyField(DEK, default=1, related_name='agora_topic_dek')
    data_kek = models.ManyToManyField(KEK, default=1, related_name='agora_topic_kek')

    objects = Librarian()

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topics'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'agora_topic_detail',
            kwargs={
                'category_slug': self.category.slug,
                'pk': self.pk,
                'slug': self.slug,
            },
        )

    def get_reply_count(self):
        """Return the number of replies to this topic."""
        return self.replies.count()

    def get_last_reply(self):
        """Return the most recent reply, or None."""
        return self.replies.order_by('-pub_date').first()


class Reply(SecureNotePublic):
    """
    A reply to a forum topic. Encrypted at rest via the Daily Planet model.
    Supports nesting via self-referential parent FK.
    """
    author = models.ForeignKey(
        AgoraProfile,
        on_delete=models.CASCADE,
        related_name='replies',
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='replies',
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
    )

    # Override inherited M2M fields with unique related_names
    data_dek = models.ManyToManyField(DEK, default=1, related_name='agora_reply_dek')
    data_kek = models.ManyToManyField(KEK, default=1, related_name='agora_reply_kek')

    objects = Librarian()

    class Meta:
        verbose_name = 'reply'
        verbose_name_plural = 'replies'
        ordering = ['pub_date']

    def __str__(self):
        return f'Reply by {self.author.handle} on {self.topic.title}'

    def get_children(self):
        """Return direct child replies."""
        return Reply.objects.filter(parent=self)

    def get_depth(self):
        """Return nesting depth (0 = top-level reply). Capped at 4."""
        depth = 0
        current = self
        while current.parent is not None and depth < 4:
            depth += 1
            current = current.parent
        return depth
