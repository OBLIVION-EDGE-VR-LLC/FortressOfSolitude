"""Views for the Research section — public read, authenticated write."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View

from _FortressOfSolitude.agora.views import AgoraProfileRequiredMixin
from .forms import ResearchPostForm
from .models import ResearchPost


class ResearchListView(View):
    """Public list of all research posts — no login required."""

    def get(self, request):
        posts = ResearchPost.objects.all().select_related('author')
        return render(request, 'research/research_list.html', {
            'posts': posts,
        })


class ResearchDetailView(View):
    """Public detail view of a research post — no login required."""

    def get(self, request, pk, slug):
        post = get_object_or_404(ResearchPost, pk=pk)
        return render(request, 'research/research_detail.html', {
            'post': post,
            'object': post,
        })


class ResearchCreateView(AgoraProfileRequiredMixin, View):
    """Create a research post — requires login + AgoraProfile."""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = ResearchPostForm()
        return render(request, 'research/research_form.html', {'form': form})

    def post(self, request):
        form = ResearchPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.agora_profile
            post.save()
            # Encrypt using Daily Planet shared key
            ResearchPost.objects._encrypt_Daily_Planet_Note(
                password=request.user.password,
                secure_text=post.secure_text,
                postobj=post,
                request=request,
            )
            return redirect(post.get_absolute_url())
        return render(request, 'research/research_form.html', {'form': form})
