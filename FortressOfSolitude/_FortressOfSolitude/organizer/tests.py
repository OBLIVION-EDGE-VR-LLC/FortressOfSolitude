"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import UserFolder
from _FortressOfSolitude.NeutrinoKey.models import KEK, DEK

User = get_user_model()


class UserFolderModelTest(TestCase):
    """Tests for the UserFolder model."""

    def setUp(self):
        self.user = User(email='clark@dailyplanet.com', is_active=True)
        self.user.set_password('krypt0n_r0cks_2022!')
        self.user.save(using='default')
        self.password = b'krypt0n_r0cks_2022!'

    def test_create_root_creates_folder_tree(self):
        """Creating a root folder produces root + default subfolders."""
        root = UserFolder.create_root_for_user(self.user, self.password)
        self.assertIsNotNone(root.pk)
        self.assertEqual(root.name, 'root')
        self.assertEqual(root.owner, self.user)
        self.assertIsNone(root.parent)
        self.assertIsNotNone(root.kek)
        self.assertIsNotNone(root.dek)
        # Default subfolders created
        children = UserFolder.objects.filter(parent=root)
        child_names = set(children.values_list('name', flat=True))
        self.assertIn('journal', child_names)
        self.assertIn('projects', child_names)
        self.assertIn('music', child_names)
        self.assertIn('files', child_names)
        self.assertIn('inbox', child_names)
        self.assertEqual(children.count(), 5)

    def test_each_subfolder_has_own_dek(self):
        """Each subfolder gets its own DEK (per-scope encryption)."""
        root = UserFolder.create_root_for_user(self.user, self.password)
        children = UserFolder.objects.filter(parent=root)
        dek_ids = set(children.values_list('dek_id', flat=True))
        # All DEK IDs should be unique (each folder has its own)
        self.assertEqual(len(dek_ids), 5)

    def test_subfolders_share_parent_kek(self):
        """All subfolders under root share the root's KEK."""
        root = UserFolder.create_root_for_user(self.user, self.password)
        children = UserFolder.objects.filter(parent=root)
        kek_ids = set(children.values_list('kek_id', flat=True))
        # All should use the root's KEK
        self.assertEqual(kek_ids, {root.kek_id})

    def test_get_children(self):
        """get_children returns direct child folders."""
        root = UserFolder.create_root_for_user(self.user, self.password)
        children = root.get_children()
        self.assertEqual(children.count(), 5)

    def test_get_breadcrumbs(self):
        """get_breadcrumbs returns path from root to current folder."""
        root = UserFolder.create_root_for_user(self.user, self.password)
        journal = UserFolder.objects.get(parent=root, name='journal')
        breadcrumbs = journal.get_breadcrumbs()
        self.assertEqual(len(breadcrumbs), 2)
        self.assertEqual(breadcrumbs[0], root)
        self.assertEqual(breadcrumbs[1], journal)

    def test_create_custom_subfolder(self):
        """Users can create custom subfolders inside existing ones."""
        root = UserFolder.create_root_for_user(self.user, self.password)
        projects = UserFolder.objects.get(parent=root, name='projects')
        custom = UserFolder.create_subfolder(
            parent=projects,
            name='alpha-project',
            password=self.password,
        )
        self.assertIsNotNone(custom.pk)
        self.assertEqual(custom.parent, projects)
        self.assertEqual(custom.owner, self.user)
        self.assertEqual(custom.kek, root.kek)  # shares root KEK
        self.assertNotEqual(custom.dek_id, projects.dek_id)  # own DEK

    def test_no_duplicate_root_for_same_user(self):
        """Creating root twice for same user returns existing root."""
        root1 = UserFolder.create_root_for_user(self.user, self.password)
        root2 = UserFolder.create_root_for_user(self.user, self.password)
        self.assertEqual(root1.pk, root2.pk)


class FileFolderAssociationTest(TestCase):
    """Tests for file-to-folder association."""

    def setUp(self):
        self.user = User(email='lois@dailyplanet.com', is_active=True)
        self.user.set_password('m3tr0p0l1s!')
        self.user.save(using='default')
        self.password = b'm3tr0p0l1s!'
        self.root = UserFolder.create_root_for_user(self.user, self.password)

    def test_imagefile_can_have_folder(self):
        """ImageFile can be associated with a folder."""
        from .models import ImageFile
        photos_folder = UserFolder.objects.get(parent=self.root, name='files')
        # ImageFile has a nullable folder FK
        self.assertTrue(hasattr(ImageFile, 'folder'))

    def test_folder_field_is_nullable(self):
        """Folder FK is nullable for backward compatibility."""
        from .models import ImageFile
        field = ImageFile._meta.get_field('folder')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)


from django.test import Client


class FolderBrowserViewTest(TestCase):
    """Tests for the folder browser view."""

    def setUp(self):
        self.user = User(email='diana@themyscira.org', is_active=True)
        self.user.set_password('amaz0n_pr1nc3ss!')
        self.user.save(using='default')
        self.password = b'amaz0n_pr1nc3ss!'
        self.root = UserFolder.create_root_for_user(self.user, self.password)
        self.client = Client()
        self.client.login(email='diana@themyscira.org', password='amaz0n_pr1nc3ss!')

    def test_folder_root_returns_200(self):
        """Root folder browser returns 200 for authenticated user."""
        response = self.client.get('/folders/')
        self.assertEqual(response.status_code, 200)

    def test_folder_root_shows_subfolders(self):
        """Root folder view shows default subfolders."""
        response = self.client.get('/folders/')
        content = response.content.decode()
        self.assertIn('journal', content)
        self.assertIn('projects', content)
        self.assertIn('music', content)
        self.assertIn('files', content)
        self.assertIn('inbox', content)

    def test_subfolder_view_returns_200(self):
        """Viewing a subfolder returns 200."""
        journal = UserFolder.objects.get(parent=self.root, name='journal')
        response = self.client.get(f'/folders/{journal.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_subfolder_shows_breadcrumbs(self):
        """Subfolder view shows breadcrumb navigation."""
        journal = UserFolder.objects.get(parent=self.root, name='journal')
        response = self.client.get(f'/folders/{journal.pk}/')
        content = response.content.decode()
        self.assertIn('root', content)
        self.assertIn('journal', content)

    def test_unauthenticated_redirects(self):
        """Unauthenticated users are redirected to login."""
        anon = Client()
        response = anon.get('/folders/')
        self.assertEqual(response.status_code, 302)

    def test_other_user_cannot_see_folders(self):
        """Users cannot browse another user's folders."""
        other = User(email='bruce@waynetech.com', is_active=True)
        other.set_password('g0tham!')
        other.save(using='default')
        other_root = UserFolder.create_root_for_user(other, b'g0tham!')
        # Diana tries to access Bruce's folder
        response = self.client.get(f'/folders/{other_root.pk}/')
        self.assertEqual(response.status_code, 404)


class UploadWithFolderTest(TestCase):
    """Tests for uploading files into a folder."""

    def setUp(self):
        self.user = User(email='hal@oa.com', is_active=True)
        self.user.set_password('gr33n_l4nt3rn!')
        self.user.save(using='default')
        self.root = UserFolder.create_root_for_user(self.user, b'gr33n_l4nt3rn!')
        self.client = Client()
        self.client.login(email='hal@oa.com', password='gr33n_l4nt3rn!')

    def test_upload_form_includes_folder_field(self):
        """Upload form has a folder selection field."""
        from .forms import UploadFileForm
        form = UploadFileForm(user=self.user)
        self.assertIn('folder', form.fields)

    def test_upload_form_only_shows_user_folders(self):
        """Folder dropdown only shows the current user's folders."""
        other = User(email='sinestro@qward.com', is_active=True)
        other.set_password('f34r_p0w3r!')
        other.save(using='default')
        UserFolder.create_root_for_user(other, b'f34r_p0w3r!')

        from .forms import UploadFileForm
        form = UploadFileForm(user=self.user)
        folder_qs = form.fields['folder'].queryset
        for folder in folder_qs:
            self.assertEqual(folder.owner, self.user)
