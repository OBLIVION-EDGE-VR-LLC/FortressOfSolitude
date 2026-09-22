"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import AgoraProfile, Category

User = get_user_model()


class AgoraProfileModelTest(TestCase):
    """Tests for the AgoraProfile model."""

    def setUp(self):
        self.user = User(email='clark@dailyplanet.com', is_active=True)
        self.user.set_password('krypt0n_r0cks_2022!')
        self.user.save(using='default')

    def test_create_profile(self):
        """Can create an AgoraProfile for a user."""
        profile = AgoraProfile.objects.create(
            user=self.user,
            handle='kal-el',
            about_me='Last son of Krypton.',
            favorite_movie='Man of Steel',
            favorite_song='Hero',
            favorite_artist='Chad Kroeger',
            quote='Hope is not a strategy, but it is a start.',
        )
        self.assertIsNotNone(profile.pk)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.handle, 'kal-el')

    def test_handle_is_unique(self):
        """Two profiles cannot have the same handle."""
        AgoraProfile.objects.create(user=self.user, handle='kal-el')
        other_user = User(email='lois@dailyplanet.com', is_active=True)
        other_user.set_password('m3tr0p0l1s!')
        other_user.save(using='default')
        with self.assertRaises(Exception):
            AgoraProfile.objects.create(user=other_user, handle='kal-el')

    def test_one_profile_per_user(self):
        """A user can only have one AgoraProfile."""
        AgoraProfile.objects.create(user=self.user, handle='kal-el')
        with self.assertRaises(Exception):
            AgoraProfile.objects.create(user=self.user, handle='superman')

    def test_str_returns_handle(self):
        """String representation is the handle."""
        profile = AgoraProfile.objects.create(user=self.user, handle='kal-el')
        self.assertEqual(str(profile), 'kal-el')

    def test_optional_fields_default_blank(self):
        """Profile fields besides handle are optional."""
        profile = AgoraProfile.objects.create(user=self.user, handle='kal-el')
        self.assertEqual(profile.about_me, '')
        self.assertEqual(profile.favorite_movie, '')
        self.assertEqual(profile.favorite_song, '')
        self.assertEqual(profile.favorite_artist, '')
        self.assertEqual(profile.quote, '')


class CategoryModelTest(TestCase):
    """Tests for the Category model."""

    def test_create_category(self):
        """Can create a forum category."""
        cat = Category.objects.create(
            name='Discussion Boards',
            slug='discussion-boards',
            description='Open discourse on any topic.',
        )
        self.assertIsNotNone(cat.pk)
        self.assertEqual(cat.name, 'Discussion Boards')
        self.assertEqual(cat.slug, 'discussion-boards')

    def test_slug_is_unique(self):
        """Category slugs must be unique."""
        Category.objects.create(name='A', slug='a-slug', description='A')
        with self.assertRaises(Exception):
            Category.objects.create(name='B', slug='a-slug', description='B')

    def test_str_returns_name(self):
        """String representation is the category name."""
        cat = Category.objects.create(
            name='Creative Showcase',
            slug='creative-showcase',
            description='Share creative works.',
        )
        self.assertEqual(str(cat), 'Creative Showcase')

    def test_ordering_by_name(self):
        """Categories are ordered alphabetically by name."""
        Category.objects.create(name='Zebra', slug='zebra', description='z')
        Category.objects.create(name='Alpha', slug='alpha', description='a')
        cats = list(Category.objects.values_list('name', flat=True))
        self.assertEqual(cats, ['Alpha', 'Zebra'])


from _FortressOfSolitude.NeutrinoKey.models import DEK, KEK


class TopicModelTest(TestCase):
    """Tests for the Topic model."""

    def setUp(self):
        self.user = User(email='diana@themyscira.org', is_active=True)
        self.user.set_password('amaz0n_pr1nc3ss!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user, handle='wonder-woman',
        )
        self.category = Category.objects.create(
            name='Discussion Boards',
            slug='discussion-boards',
            description='Open discourse.',
        )

    def test_create_topic(self):
        """Can create a Topic in a category."""
        from .models import Topic
        topic = Topic(
            title='The Future of Themyscira',
            slug='future-themyscira',
            secure_text='We need to discuss our defenses.',
            author=self.profile,
            category=self.category,
        )
        topic.save()
        self.assertIsNotNone(topic.pk)
        self.assertEqual(topic.author.handle, 'wonder-woman')
        self.assertEqual(topic.category, self.category)

    def test_topic_defaults(self):
        """Topic defaults: not pinned, not locked, zero views."""
        from .models import Topic
        topic = Topic.objects.create(
            title='Defaults Test',
            slug='defaults-test',
            author=self.profile,
            category=self.category,
        )
        self.assertFalse(topic.is_pinned)
        self.assertFalse(topic.is_locked)
        self.assertEqual(topic.view_count, 0)

    def test_get_reply_count_zero(self):
        """Topic with no replies returns 0."""
        from .models import Topic
        topic = Topic.objects.create(
            title='No Replies',
            slug='no-replies',
            author=self.profile,
            category=self.category,
        )
        self.assertEqual(topic.get_reply_count(), 0)

    def test_get_reply_count_with_replies(self):
        """Topic reply count reflects actual replies."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='With Replies',
            slug='with-replies',
            author=self.profile,
            category=self.category,
        )
        Reply.objects.create(
            title='Re: With Replies',
            slug='re-with-replies-1',
            author=self.profile,
            topic=topic,
        )
        Reply.objects.create(
            title='Re: With Replies 2',
            slug='re-with-replies-2',
            author=self.profile,
            topic=topic,
        )
        self.assertEqual(topic.get_reply_count(), 2)

    def test_get_last_reply(self):
        """get_last_reply returns the most recent reply."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='Last Reply Test',
            slug='last-reply-test',
            author=self.profile,
            category=self.category,
        )
        Reply.objects.create(
            title='First',
            slug='first-reply',
            author=self.profile,
            topic=topic,
        )
        last = Reply.objects.create(
            title='Second',
            slug='second-reply',
            author=self.profile,
            topic=topic,
        )
        self.assertEqual(topic.get_last_reply(), last)

    def test_get_last_reply_none(self):
        """get_last_reply returns None when no replies exist."""
        from .models import Topic
        topic = Topic.objects.create(
            title='No Reply',
            slug='no-reply',
            author=self.profile,
            category=self.category,
        )
        self.assertIsNone(topic.get_last_reply())


class ReplyModelTest(TestCase):
    """Tests for the Reply model."""

    def setUp(self):
        self.user = User(email='bruce@waynetech.com', is_active=True)
        self.user.set_password('g0tham_kn1ght!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user, handle='dark-knight',
        )
        self.category = Category.objects.create(
            name='Knowledge Exchange',
            slug='knowledge-exchange',
            description='Q&A and peer learning.',
        )

    def test_create_reply(self):
        """Can create a Reply to a Topic."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='Gotham Security',
            slug='gotham-security',
            author=self.profile,
            category=self.category,
        )
        reply = Reply.objects.create(
            title='Re: Gotham Security',
            slug='re-gotham-security',
            author=self.profile,
            topic=topic,
        )
        self.assertIsNotNone(reply.pk)
        self.assertEqual(reply.topic, topic)
        self.assertIsNone(reply.parent)

    def test_nested_reply(self):
        """Can create a nested reply (reply to a reply)."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='Nested Test',
            slug='nested-test',
            author=self.profile,
            category=self.category,
        )
        parent_reply = Reply.objects.create(
            title='Parent Reply',
            slug='parent-reply',
            author=self.profile,
            topic=topic,
        )
        child_reply = Reply.objects.create(
            title='Child Reply',
            slug='child-reply',
            author=self.profile,
            topic=topic,
            parent=parent_reply,
        )
        self.assertEqual(child_reply.parent, parent_reply)

    def test_get_children(self):
        """get_children returns direct child replies."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='Children Test',
            slug='children-test',
            author=self.profile,
            category=self.category,
        )
        parent_reply = Reply.objects.create(
            title='Parent',
            slug='parent-r',
            author=self.profile,
            topic=topic,
        )
        Reply.objects.create(
            title='Child 1',
            slug='child-1',
            author=self.profile,
            topic=topic,
            parent=parent_reply,
        )
        Reply.objects.create(
            title='Child 2',
            slug='child-2',
            author=self.profile,
            topic=topic,
            parent=parent_reply,
        )
        self.assertEqual(parent_reply.get_children().count(), 2)

    def test_get_depth_root_reply(self):
        """A top-level reply has depth 0."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='Depth Test',
            slug='depth-test',
            author=self.profile,
            category=self.category,
        )
        reply = Reply.objects.create(
            title='Top Level',
            slug='top-level',
            author=self.profile,
            topic=topic,
        )
        self.assertEqual(reply.get_depth(), 0)

    def test_get_depth_nested(self):
        """Nested replies have correct depth."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='Deep Depth Test',
            slug='deep-depth-test',
            author=self.profile,
            category=self.category,
        )
        r1 = Reply.objects.create(
            title='Level 0', slug='level-0',
            author=self.profile, topic=topic,
        )
        r2 = Reply.objects.create(
            title='Level 1', slug='level-1',
            author=self.profile, topic=topic, parent=r1,
        )
        r3 = Reply.objects.create(
            title='Level 2', slug='level-2',
            author=self.profile, topic=topic, parent=r2,
        )
        self.assertEqual(r1.get_depth(), 0)
        self.assertEqual(r2.get_depth(), 1)
        self.assertEqual(r3.get_depth(), 2)

    def test_reply_ordering_chronological(self):
        """Replies are ordered by pub_date ascending."""
        from .models import Topic, Reply
        topic = Topic.objects.create(
            title='Order Test',
            slug='order-test',
            author=self.profile,
            category=self.category,
        )
        r1 = Reply.objects.create(
            title='First', slug='first-r',
            author=self.profile, topic=topic,
        )
        r2 = Reply.objects.create(
            title='Second', slug='second-r',
            author=self.profile, topic=topic,
        )
        replies = list(Reply.objects.filter(topic=topic))
        self.assertEqual(replies[0], r1)
        self.assertEqual(replies[1], r2)


class CategorySeedTest(TestCase):
    """Test that core categories are seeded."""

    def test_four_core_categories_exist(self):
        """The four core Agora categories exist."""
        slugs = set(Category.objects.values_list('slug', flat=True))
        self.assertIn('discussion-boards', slugs)
        self.assertIn('creative-showcase', slugs)
        self.assertIn('collaborative-projects', slugs)
        self.assertIn('knowledge-exchange', slugs)


from django.test import Client


class AgoraProfileSetupViewTest(TestCase):
    """Tests for the profile setup view."""

    def setUp(self):
        self.user = User(email='hal@oa.com', is_active=True)
        self.user.set_password('gr33n_l4nt3rn!')
        self.user.save(using='default')
        self.client = Client()
        self.client.login(email='hal@oa.com', password='gr33n_l4nt3rn!')

    def test_setup_page_returns_200(self):
        """Setup page returns 200 for authenticated user without profile."""
        response = self.client.get('/agora/setup/')
        self.assertEqual(response.status_code, 200)

    def test_setup_creates_profile(self):
        """Submitting the setup form creates an AgoraProfile."""
        response = self.client.post('/agora/setup/', {
            'handle': 'green-lantern',
            'about_me': 'In brightest day.',
            'favorite_movie': 'Green Lantern',
            'favorite_song': '',
            'favorite_artist': '',
            'quote': 'In brightest day, in blackest night.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AgoraProfile.objects.filter(user=self.user).exists())
        self.assertEqual(
            AgoraProfile.objects.get(user=self.user).handle,
            'green-lantern',
        )

    def test_setup_redirects_if_already_has_profile(self):
        """Users who already have a profile are redirected from setup."""
        AgoraProfile.objects.create(user=self.user, handle='gl')
        response = self.client.get('/agora/setup/')
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_redirects(self):
        """Unauthenticated users are redirected to login."""
        anon = Client()
        response = anon.get('/agora/setup/')
        self.assertEqual(response.status_code, 302)


class AgoraGatingTest(TestCase):
    """Tests for the AgoraProfileRequiredMixin gating."""

    def setUp(self):
        self.user = User(email='barry@starlab.com', is_active=True)
        self.user.set_password('sp33dst3r!')
        self.user.save(using='default')
        self.client = Client()
        self.client.login(email='barry@starlab.com', password='sp33dst3r!')

    def test_landing_redirects_to_setup_without_profile(self):
        """Agora landing redirects to setup if user has no profile."""
        response = self.client.get('/agora/')
        self.assertRedirects(response, '/agora/setup/')

    def test_landing_accessible_with_profile(self):
        """Agora landing is accessible when user has a profile."""
        AgoraProfile.objects.create(user=self.user, handle='flash')
        response = self.client.get('/agora/')
        self.assertEqual(response.status_code, 200)


class AgoraProfileDetailViewTest(TestCase):
    """Tests for the profile detail view."""

    def setUp(self):
        self.user = User(email='arthur@atlantis.com', is_active=True)
        self.user.set_password('tr1d3nt_k1ng!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user,
            handle='aquaman',
            about_me='King of Atlantis.',
            favorite_movie='Aquaman',
            quote='The sea does not dream of you.',
        )
        self.client = Client()
        self.client.login(email='arthur@atlantis.com', password='tr1d3nt_k1ng!')

    def test_profile_detail_returns_200(self):
        """Profile detail page returns 200."""
        response = self.client.get('/agora/profile/aquaman/')
        self.assertEqual(response.status_code, 200)

    def test_profile_detail_shows_handle(self):
        """Profile detail shows the user's handle."""
        response = self.client.get('/agora/profile/aquaman/')
        self.assertContains(response, 'aquaman')

    def test_profile_detail_shows_about(self):
        """Profile detail shows the about_me text."""
        response = self.client.get('/agora/profile/aquaman/')
        self.assertContains(response, 'King of Atlantis.')

    def test_nonexistent_profile_returns_404(self):
        """Non-existent handle returns 404."""
        response = self.client.get('/agora/profile/nobody/')
        self.assertEqual(response.status_code, 404)


class CategoryDetailViewTest(TestCase):
    """Tests for the category detail view."""

    def setUp(self):
        self.user = User(email='victor@starlab.com', is_active=True)
        self.user.set_password('cyb0rg_t33n!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user, handle='cyborg',
        )
        self.category, _ = Category.objects.get_or_create(
            slug='discussion-boards',
            defaults={
                'name': 'Discussion Boards',
                'description': 'Open discourse.',
            },
        )
        self.client = Client()
        self.client.login(email='victor@starlab.com', password='cyb0rg_t33n!')

    def test_category_detail_returns_200(self):
        """Category detail page returns 200."""
        response = self.client.get('/agora/discussion-boards/')
        self.assertEqual(response.status_code, 200)

    def test_category_detail_shows_category_name(self):
        """Category detail shows the category name."""
        response = self.client.get('/agora/discussion-boards/')
        self.assertContains(response, 'Discussion Boards')

    def test_category_detail_lists_topics(self):
        """Category detail lists topics in the category."""
        from .models import Topic
        Topic.objects.create(
            title='Test Topic',
            slug='test-topic',
            author=self.profile,
            category=self.category,
        )
        response = self.client.get('/agora/discussion-boards/')
        self.assertContains(response, 'Test Topic')

    def test_nonexistent_category_returns_404(self):
        """Non-existent category slug returns 404."""
        response = self.client.get('/agora/nonexistent/')
        self.assertEqual(response.status_code, 404)


class TopicCreateViewTest(TestCase):
    """Tests for the topic create view."""

    def setUp(self):
        self.user = User(email='kara@krypton.com', is_active=True)
        self.user.set_password('sup3rg1rl!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user, handle='supergirl',
        )
        self.category, _ = Category.objects.get_or_create(
            slug='knowledge-exchange',
            defaults={
                'name': 'Knowledge Exchange',
                'description': 'Learn and teach.',
            },
        )
        self.client = Client()
        self.client.login(email='kara@krypton.com', password='sup3rg1rl!')

    def test_topic_create_form_returns_200(self):
        """Topic create form returns 200."""
        response = self.client.get('/agora/knowledge-exchange/new/')
        self.assertEqual(response.status_code, 200)

    def test_topic_create_redirects_on_success(self):
        """Creating a topic redirects to the topic detail."""
        response = self.client.post('/agora/knowledge-exchange/new/', {
            'title': 'Kryptonian History',
            'slug': 'kryptonian-history',
            'secure_text': 'The history of Krypton is vast.',
        })
        self.assertEqual(response.status_code, 302)
        from .models import Topic
        self.assertTrue(Topic.objects.filter(slug='kryptonian-history').exists())

    def test_topic_create_sets_author_and_category(self):
        """Created topic has correct author and category."""
        self.client.post('/agora/knowledge-exchange/new/', {
            'title': 'Author Test',
            'slug': 'author-test',
            'secure_text': 'Testing author assignment.',
        })
        from .models import Topic
        topic = Topic.objects.get(slug='author-test')
        self.assertEqual(topic.author, self.profile)
        self.assertEqual(topic.category, self.category)


class TopicDetailViewTest(TestCase):
    """Tests for the topic detail view."""

    def setUp(self):
        self.user = User(email='oliver@starling.com', is_active=True)
        self.user.set_password('gr33n_4rr0w!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user, handle='green-arrow',
        )
        self.category, _ = Category.objects.get_or_create(
            slug='discussion-boards',
            defaults={
                'name': 'Discussion Boards',
                'description': 'Open discourse.',
            },
        )
        from .models import Topic
        self.topic = Topic.objects.create(
            title='Star City Politics',
            slug='star-city-politics',
            author=self.profile,
            category=self.category,
            secure_text='We need to talk about the mayor.',
        )
        self.client = Client()
        self.client.login(email='oliver@starling.com', password='gr33n_4rr0w!')

    def test_topic_detail_returns_200(self):
        """Topic detail page returns 200."""
        response = self.client.get(
            f'/agora/discussion-boards/{self.topic.pk}-star-city-politics/'
        )
        self.assertEqual(response.status_code, 200)

    def test_topic_detail_shows_title(self):
        """Topic detail shows the topic title."""
        response = self.client.get(
            f'/agora/discussion-boards/{self.topic.pk}-star-city-politics/'
        )
        self.assertContains(response, 'Star City Politics')

    def test_topic_detail_increments_view_count(self):
        """Viewing a topic increments view_count."""
        from .models import Topic
        self.client.get(
            f'/agora/discussion-boards/{self.topic.pk}-star-city-politics/'
        )
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.view_count, 1)


class ReplyCreateViewTest(TestCase):
    """Tests for the reply create view."""

    def setUp(self):
        self.user = User(email='shayera@thanagar.com', is_active=True)
        self.user.set_password('hawk_g1rl!')
        self.user.save(using='default')
        self.profile = AgoraProfile.objects.create(
            user=self.user, handle='hawkgirl',
        )
        self.category, _ = Category.objects.get_or_create(
            slug='discussion-boards',
            defaults={
                'name': 'Discussion Boards',
                'description': 'Open discourse.',
            },
        )
        from .models import Topic
        self.topic = Topic.objects.create(
            title='Thanagarian Tactics',
            slug='thanagarian-tactics',
            author=self.profile,
            category=self.category,
        )
        self.client = Client()
        self.client.login(email='shayera@thanagar.com', password='hawk_g1rl!')

    def test_reply_creates_reply(self):
        """Posting a reply creates a Reply object."""
        from .models import Reply
        url = f'/agora/discussion-boards/{self.topic.pk}-thanagarian-tactics/reply/'
        response = self.client.post(url, {
            'secure_text': 'Nth metal is the key.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reply.objects.filter(topic=self.topic).count(), 1)

    def test_reply_sets_author(self):
        """Reply has the correct author."""
        from .models import Reply
        url = f'/agora/discussion-boards/{self.topic.pk}-thanagarian-tactics/reply/'
        self.client.post(url, {'secure_text': 'Author test.'})
        reply = Reply.objects.get(topic=self.topic)
        self.assertEqual(reply.author, self.profile)

    def test_locked_topic_rejects_reply(self):
        """Cannot reply to a locked topic."""
        from .models import Reply
        self.topic.is_locked = True
        self.topic.save()
        url = f'/agora/discussion-boards/{self.topic.pk}-thanagarian-tactics/reply/'
        response = self.client.post(url, {'secure_text': 'Should fail.'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Reply.objects.filter(topic=self.topic).count(), 0)


class NavBarAgoraLinkTest(TestCase):
    """Test that The Agora link appears in nav bars."""

    def setUp(self):
        from django.contrib.auth.models import Permission
        self.user = User(email='john@oa.com', is_active=True)
        self.user.set_password('m4rt14n!')
        self.user.save(using='default')
        perm = Permission.objects.get(codename='view_post')
        self.user.user_permissions.add(perm)
        self.client = Client()
        self.client.login(email='john@oa.com', password='m4rt14n!')

    def test_blog_base_has_agora_link(self):
        """Blog base template includes The Agora link."""
        response = self.client.get('/blog/')
        self.assertContains(response, 'The Agora')
