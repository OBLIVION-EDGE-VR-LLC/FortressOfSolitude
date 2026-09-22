'''
DBA 1337_TECH, AUSTIN TEXAS © MAY 2020
Proof of Concept code, No liabilities or warranties expressed or implied.
'''
from datetime import date

from django.db import models

from django.urls import reverse, reverse_lazy
import _FortressOfSolitude.settings as settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from _FortressOfSolitude.organizer.models import Startup, Tag, Tasking, SecureNote
from _FortressOfSolitude.core.managers import Librarian
from _FortressOfSolitude.core.models import SecureNotePublic


# Create your models here.

class PostQueryset(models.QuerySet):

    def published(self):
        return self.filter(
            pub_date__lte=date.today())


'''
Base Post Manager for unencrypted text model
input None
'''


class BasePostManager(models.Manager):

    def get_queryset(self):
        return (
            PostQueryset(
                self.model,
                using=self._db,
                hints=self._hints))

    def get_by_natural_key(self, pub_date, slug):
        return self.get(
            pub_date=pub_date,
            slug=slug)


class SecurePostManager(models.Manager):

    def get_queryset(self):
        return PostQueryset(
            self.model,
            using=self._db,
            hints=self._hints)

    def get_by_natural_key(self, pub_date, slug):
        return self.get(
            pub_date=pub_date,
            slug=slug)


PostManager = BasePostManager.from_queryset(
    PostQueryset)


class SecureDataAtRestPost(SecureNote):
    author = models.ForeignKey(
        get_user_model(),
        related_name='secureblog_posts',
        on_delete=models.CASCADE,
        default=1)
    tags = models.ManyToManyField(Tag, related_name='secureblog_posts')
    tasking = models.ManyToManyField(Tasking, related_name='securetasking')
    is_encrypted = models.BooleanField(default=True)

    objects = Librarian()

    class Meta:
        verbose_name = '[Secure] blog post'
        ordering = ['-pub_date', 'title']
        get_latest_by = 'pub_date'
        permissions = (
            ("view_future_post",
             "Can view unpublished Post"),
            ("add_tasking",
             "Can add task"),
        )

    def __str__(self):
        return "{} on {}".format(
            self.title,
            self.pub_date.strftime('%Y-%m-%d'))

    def get_absolute_url(self):
        return reverse(
            'blog_securepost_detail',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def get_archive_month_url(self):
        return reverse(
            'blog_securepost_archive_month',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month})

    def get_archive_year_url(self):
        print(f'{self.pub_date.year}')
        return reverse(
            'blog_securepost_archive_year',
            kwargs={'year': self.pub_date.year})

    def get_delete_url(self):
        return reverse(
            'blog_securepost_delete',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def get_update_url(self):
        return reverse(
            'blog_securepost_update',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def natural_key(self):
        return (
            self.pub_date,
            self.slug)

    natural_key.dependencies = [
        'user.user',
    ]

    def formatted_title(self):
        return self.title.title()

    def short_text(self):
        if len(self.text) > 20:
            short = ' '.join(self.text.split()[:20])
            short += ' ...'
        else:
            short = self.text
        return short


class SecureDataAtRestPostPublic(SecureNotePublic):
    author = models.ForeignKey(
        get_user_model(),
        related_name='secureblog_public_posts_author',
        on_delete=models.CASCADE,
        default=1)
    tags = models.ManyToManyField(Tag, related_name='secureblog_public_posts_tags')
    tasking = models.ManyToManyField(Tasking, related_name='securetasking_public')
    is_encrypted = models.BooleanField(default=True)

    objects = Librarian()

    class Meta:
        verbose_name = '[Secure] blog public post'
        ordering = ['-pub_date', 'title']
        get_latest_by = 'pub_date'
        permissions = (
            ("view_future_post",
             "Can view unpublished Post"),
            ("add_tasking",
             "Can add task"),
        )

    def __str__(self):
        return "{} on {}".format(
            self.title,
            self.pub_date.strftime('%Y-%m-%d'))

    def get_absolute_url(self):
        return reverse(
            'blog_securepost_public_detail',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def get_archive_month_url(self):
        return reverse(
            'blog_securepost_public_archive_month',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month})

    def get_archive_year_url(self):
        print(f'{self.pub_date.year}')
        return reverse(
            'blog_securepost_public_archive_year',
            kwargs={'year': self.pub_date.year})

    def get_delete_url(self):
        return reverse(
            'blog_securepost_public_delete',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def get_update_url(self):
        return reverse(
            'blog_securepost_public_update',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def natural_key(self):
        return (
            self.pub_date,
            self.slug)

    natural_key.dependencies = [
        'user.user',
    ]

    def formatted_title(self):
        return self.title.title()

    def short_text(self):
        if len(self.text) > 20:
            short = ' '.join(self.text.split()[:20])
            short += ' ...'
        else:
            short = self.text
        return short


class Post(models.Model):
    """
    class Post of models.Model type class extension.  includes title, slug, author, text, pub_date, tags, and tasking
    """
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, help_text='A label for URL config', unique_for_month='pub_date')
    author = models.ForeignKey(
        get_user_model(),
        related_name='blog_posts',
        on_delete=models.CASCADE,
        default=1)
    text = models.TextField()
    pub_date = models.DateField('date published', auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='blog_posts')
    tasking = models.ManyToManyField(Tasking, related_name='tasking')

    objects = PostManager()

    class Meta:
        verbose_name = 'blog post'
        ordering = ['-pub_date', 'title']
        get_latest_by = 'pub_date'
        permissions = (
            ("view_future_post",
             "Can view unpublished Post"),
            ("add_tasking",
             "Can add task"),
        )

    def __str__(self):
        return "{} on {}".format(
            self.title,
            self.pub_date.strftime('%Y-%m-%d'))

    def get_absolute_url(self):
        return reverse(
            'blog_post_detail',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def get_archive_month_url(self):
        return reverse(
            'blog_post_archive_month',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month})

    def get_archive_year_url(self):
        return reverse(
            'blog_post_archive_year',
            kwargs={'year': self.pub_date.year})

    def get_delete_url(self):
        return reverse(
            'blog_post_delete',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def get_update_url(self):
        return reverse(
            'blog_post_update',
            kwargs={'year': self.pub_date.year,
                    'month': self.pub_date.month,
                    'slug': self.slug})

    def natural_key(self):
        return (
            self.pub_date,
            self.slug)

    natural_key.dependencies = [
        'organizer.tag',
        'user.user',
    ]

    def formatted_title(self):
        return self.title.title()

    def short_text(self):
        if len(self.text) > 20:
            short = ' '.join(self.text.split()[:20])
            short += ' ...'
        else:
            short = self.text
        return short
