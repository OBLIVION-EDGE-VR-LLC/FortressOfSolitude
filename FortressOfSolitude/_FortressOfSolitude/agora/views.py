"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.generic import View
import uuid

from .forms import AgoraProfileForm, TopicForm
from .models import AgoraProfile, Category, Topic, Reply


class AgoraProfileRequiredMixin:
    """
    Mixin that gates Agora views on having an AgoraProfile.
    Redirects to /agora/setup/ if the user has no profile.
    """

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'agora_profile'):
            return redirect('agora_profile_setup')
        try:
            request.user.agora_profile
        except AgoraProfile.DoesNotExist:
            return redirect('agora_profile_setup')
        return super().dispatch(request, *args, **kwargs)


class AgoraProfileSetupView(View):
    """First-time setup: choose handle and fill in profile."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # If user already has a profile, redirect to landing
        try:
            if hasattr(request.user, 'agora_profile') and request.user.agora_profile:
                return redirect('agora_landing')
        except AgoraProfile.DoesNotExist:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = AgoraProfileForm()
        return render(request, 'agora/profile_setup.html', {'form': form})

    def post(self, request):
        form = AgoraProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('agora_landing')
        return render(request, 'agora/profile_setup.html', {'form': form})


class AgoraProfileEditView(View):
    """Edit an existing profile."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        profile = get_object_or_404(AgoraProfile, user=request.user)
        form = AgoraProfileForm(instance=profile)
        return render(request, 'agora/profile_edit.html', {'form': form})

    def post(self, request):
        profile = get_object_or_404(AgoraProfile, user=request.user)
        form = AgoraProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('agora_profile_detail', handle=profile.handle)
        return render(request, 'agora/profile_edit.html', {'form': form})


class AgoraProfileDetailView(View):
    """View a user's public profile."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, handle):
        profile = get_object_or_404(AgoraProfile, handle=handle)
        recent_topics = profile.topics.order_by('-pub_date')[:5]
        return render(request, 'agora/profile_detail.html', {
            'profile': profile,
            'recent_topics': recent_topics,
        })


class AgoraLandingView(AgoraProfileRequiredMixin, View):
    """The Agora landing page — lists all categories."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'agora/agora_landing.html', {
            'categories': categories,
        })


class CategoryDetailView(AgoraProfileRequiredMixin, View):
    """List topics in a category, ordered by latest activity."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        topics = Topic.objects.filter(category=category).order_by(
            '-is_pinned', '-pub_date'
        )
        return render(request, 'agora/category_detail.html', {
            'category': category,
            'topics': topics,
        })


class TopicCreateView(AgoraProfileRequiredMixin, View):
    """Create a new topic in a category, encrypted via Daily Planet."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        form = TopicForm()
        return render(request, 'agora/topic_form.html', {
            'form': form,
            'category': category,
        })

    def post(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user.agora_profile
            topic.category = category
            topic.save()
            # Encrypt the text using Daily Planet shared key
            Topic.objects._encrypt_Daily_Planet_Note(
                password=request.user.password,
                secure_text=topic.secure_text,
                postobj=topic,
                request=request,
            )
            return redirect(topic.get_absolute_url())
        return render(request, 'agora/topic_form.html', {
            'form': form,
            'category': category,
        })


class TopicDetailView(AgoraProfileRequiredMixin, View):
    """View a topic and its threaded replies."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, category_slug, pk, slug):
        topic = get_object_or_404(Topic, pk=pk, category__slug=category_slug)
        # Increment view count atomically
        Topic.objects.filter(pk=pk).update(view_count=models.F('view_count') + 1)
        topic.refresh_from_db()

        replies = Reply.objects.filter(topic=topic).select_related('author', 'parent')

        return render(request, 'agora/topic_detail.html', {
            'topic': topic,
            'object': topic,
            'replies': replies,
            'category': topic.category,
        })


class ReplyCreateView(AgoraProfileRequiredMixin, View):
    """Post a reply to a topic."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, category_slug, pk, slug):
        topic = get_object_or_404(Topic, pk=pk, category__slug=category_slug)

        if topic.is_locked:
            return HttpResponseForbidden('This topic is locked.')

        secure_text = request.POST.get('secure_text', '').strip()
        if not secure_text:
            return redirect(topic.get_absolute_url())

        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            parent = Reply.objects.filter(pk=parent_id, topic=topic).first()

        # Generate a unique slug for the reply
        reply_slug = slugify(f're-{topic.slug}-{uuid.uuid4().hex[:8]}')

        reply = Reply(
            title=f'Re: {topic.title}'[:64],
            slug=reply_slug[:32],
            secure_text=secure_text,
            author=request.user.agora_profile,
            topic=topic,
            parent=parent,
        )
        reply.save()

        # Encrypt the reply text using Daily Planet shared key
        Reply.objects._encrypt_Daily_Planet_Note(
            password=request.user.password,
            secure_text=reply.secure_text,
            postobj=reply,
            request=request,
        )

        return redirect(topic.get_absolute_url())
