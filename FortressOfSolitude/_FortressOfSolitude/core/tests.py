"""Tests for the Research section."""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from _FortressOfSolitude.agora.models import AgoraProfile

User = get_user_model()


class ResearchPostModelTest(TestCase):
    """Tests for the ResearchPost model."""

    def setUp(self):
        self.user = User(email='researcher@test.com', is_active=True)
        self.user.set_password('r3s34rch!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user, handle='researcher')

    def test_create_research_post(self):
        """Can create a ResearchPost."""
        from .models import ResearchPost
        post = ResearchPost.objects.create(
            title='Test Research',
            slug='test-research',
            secure_text='Research content here.',
            author=self.profile,
            abstract='A test abstract.',
        )
        self.assertIsNotNone(post.pk)
        self.assertEqual(post.author.handle, 'researcher')


class ResearchPublicAccessTest(TestCase):
    """Tests that research is publicly accessible."""

    def test_research_list_no_login_required(self):
        """Research list is accessible without login."""
        client = Client()
        response = client.get('/research/')
        self.assertEqual(response.status_code, 200)

    def test_research_create_requires_login(self):
        """Research create redirects unauthenticated users."""
        client = Client()
        response = client.get('/research/create/')
        self.assertEqual(response.status_code, 302)

    def test_research_detail_no_login_required(self):
        """Research detail is accessible without login."""
        from .models import ResearchPost
        user = User(email='pub@test.com', is_active=True)
        user.set_password('t3st!')
        user.save(using='default')
        profile = AgoraProfile.objects.create(user=user, handle='pub-author')
        post = ResearchPost.objects.create(
            title='Public Post',
            slug='public-post',
            secure_text='Public content.',
            author=profile,
        )
        client = Client()
        response = client.get(f'/research/{post.pk}-public-post/')
        self.assertEqual(response.status_code, 200)

    def test_research_list_shows_disclaimer(self):
        """Research list page contains the public disclaimer."""
        client = Client()
        response = client.get('/research/')
        self.assertContains(response, 'publicly visible')
