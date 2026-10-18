"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

import hashlib
import os
import glob as globmod
import tempfile
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import UserFolder, ImageFile, MusicFile, MiscFile
from _FortressOfSolitude.NeutrinoKey.models import KEK, DEK
from _FortressOfSolitude.NeutrinoKey.cryptoutils import CryptoTools
from _FortressOfSolitude.core.managers import Librarian, Gor_El

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


class FileEncryptDecryptTest(TestCase):
    """Tests for encrypt/decrypt round-trip with single file storage and SHA256 naming."""

    def setUp(self):
        self.user = User(email='kalel@krypton.org', is_active=True)
        self.user.set_password('f0rtr3ss_0f_s0l1tud3!')
        self.user.save(using='default')
        self.password = str(self.user.password)
        self.plaintext_content = b'This is Kal-El secret journal entry number 42.'
        # Create a temp directory for file storage during tests
        self._tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _make_request(self, filename, content):
        """Build a fake request with FILES for the Librarian."""
        from django.test import RequestFactory
        factory = RequestFactory()
        uploaded = SimpleUploadedFile(filename, content)
        request = factory.post('/upload/', {'file_field': uploaded}, format='multipart')
        # Reset file pointer — RequestFactory may have consumed it
        uploaded.seek(0)
        request.FILES['file_field'] = uploaded
        request.user = self.user
        return request

    def test_display_name_field_exists(self):
        """All file models have a display_name field for the human-readable name."""
        for model in [ImageFile, MusicFile, MiscFile]:
            field = model._meta.get_field('display_name')
            self.assertTrue(field.null)
            self.assertEqual(field.max_length, 512)

    def test_encrypt_stores_display_name(self):
        """Encrypting a file stores the original filename in display_name."""
        request = self._make_request('superman_and_me.png', self.plaintext_content)
        with self._patch_storage(ImageFile):
            result = ImageFile.objects._encrypt_data(self.password, image_file=ImageFile(), request=request)
        self.assertEqual(result.display_name, 'superman_and_me.png')

    def test_encrypt_uses_sha256_storage_name(self):
        """The stored filename on disk uses sha256 of content, not the original name."""
        request = self._make_request('superman_and_me.png', self.plaintext_content)
        with self._patch_storage(ImageFile):
            result = ImageFile.objects._encrypt_data(self.password, image_file=ImageFile(), request=request)
        stored_name = str(result.image_file)
        # Should contain a sha256 hex digest (64 chars)
        basename = os.path.basename(stored_name)
        name_without_ext = basename.rsplit('.', 1)[0]
        self.assertEqual(len(name_without_ext), 64)
        # Should contain user id as directory prefix
        self.assertIn(str(self.user.pk), stored_name)

    def test_encrypt_creates_single_file_on_disk(self):
        """Encrypting should produce exactly one file on disk, not two."""
        request = self._make_request('fortress_log.png', self.plaintext_content)
        with self._patch_storage(ImageFile) as storage_dir:
            ImageFile.objects._encrypt_data(self.password, image_file=ImageFile(), request=request)
            # Count all files created in the storage directory tree
            files = []
            for root, dirs, filenames in os.walk(storage_dir):
                files.extend(filenames)
            self.assertEqual(len(files), 1, f"Expected 1 file on disk but found {len(files)}: {files}")

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypted file can be decrypted back to the original plaintext."""
        request = self._make_request('journal_entry.png', self.plaintext_content)
        with self._patch_storage(ImageFile):
            encrypted_obj = ImageFile.objects._encrypt_data(
                self.password, image_file=ImageFile(), request=request)
            # Decrypt within same storage context so FileField reads from temp dir
            gorel = Gor_El()
            decrypted = gorel._decrypt_data(
                self.password, image_file=encrypted_obj, request=request)
        self.assertEqual(decrypted, self.plaintext_content)

    def test_same_filename_different_users_no_collision(self):
        """Two users uploading a file with the same name get separate stored paths."""
        user2 = User(email='lois@dailyplanet.com', is_active=True)
        user2.set_password('m3tr0p0l1s_r3p0rt3r!')
        user2.save(using='default')
        password2 = str(user2.password)

        request1 = self._make_request('report.png', b'Kal-El version of the report')
        request2 = self._make_request('report.png', b'Lois version of the report')
        request2.user = user2

        with self._patch_storage(ImageFile):
            result1 = ImageFile.objects._encrypt_data(self.password, image_file=ImageFile(), request=request1)
            result2 = ImageFile.objects._encrypt_data(password2, image_file=ImageFile(), request=request2)

        # Both have the same display name
        self.assertEqual(result1.display_name, 'report.png')
        self.assertEqual(result2.display_name, 'report.png')
        # But different stored paths (different user dirs and different content hashes)
        self.assertNotEqual(str(result1.image_file), str(result2.image_file))

    def test_user_isolation_in_storage_path(self):
        """Each user's files are stored under their own user ID directory."""
        request = self._make_request('secret.png', self.plaintext_content)
        with self._patch_storage(ImageFile):
            result = ImageFile.objects._encrypt_data(self.password, image_file=ImageFile(), request=request)
        stored_path = str(result.image_file)
        # Path should start with user id prefix
        self.assertTrue(
            stored_path.startswith(f'{self.user.pk}/'),
            f"Expected path to start with '{self.user.pk}/' but got '{stored_path}'"
        )

    def test_str_returns_display_name(self):
        """__str__ returns the human-readable display_name, not the hash path."""
        request = self._make_request('my_song.png', self.plaintext_content)
        with self._patch_storage(ImageFile):
            result = ImageFile.objects._encrypt_data(self.password, image_file=ImageFile(), request=request)
        self.assertEqual(str(result), 'my_song.png')

    def _patch_storage(self, model_class):
        """Context manager to redirect file storage to temp directory."""
        from django.core.files.storage import FileSystemStorage
        from contextlib import contextmanager

        @contextmanager
        def _ctx():
            tmp_storage = FileSystemStorage(location=self._tmp)
            # Patch the storage on the model's image_file field
            original_storage = model_class.image_file.field.storage
            model_class.image_file.field.storage = tmp_storage
            try:
                yield self._tmp
            finally:
                model_class.image_file.field.storage = original_storage

        return _ctx()


class UploadFormSplitTest(TestCase):
    """Tests for the split upload forms (file vs folder)."""

    def setUp(self):
        self.user = User(email='barry@ccpd.gov', is_active=True)
        self.user.set_password('sp33df0rc3!')
        self.user.save(using='default')
        self.root = UserFolder.create_root_for_user(self.user, b'sp33df0rc3!')

    def test_file_upload_form_has_file_field_and_folder(self):
        """FileUploadForm has file_field and folder, no title."""
        from .forms import FileUploadForm
        form = FileUploadForm(user=self.user)
        self.assertIn('file_field', form.fields)
        self.assertIn('folder', form.fields)
        self.assertNotIn('title', form.fields)

    def test_folder_upload_form_has_folder_field_and_parent(self):
        """FolderUploadForm has folder_field and parent_folder."""
        from .forms import FolderUploadForm
        form = FolderUploadForm(user=self.user)
        self.assertIn('folder_field', form.fields)
        self.assertIn('parent_folder', form.fields)

    def test_folder_upload_form_only_shows_user_folders(self):
        """FolderUploadForm parent_folder only shows current user's folders."""
        other = User(email='eobard@future.com', is_active=True)
        other.set_password('r3v3rs3!')
        other.save(using='default')
        UserFolder.create_root_for_user(other, b'r3v3rs3!')

        from .forms import FolderUploadForm
        form = FolderUploadForm(user=self.user)
        for folder in form.fields['parent_folder'].queryset:
            self.assertEqual(folder.owner, self.user)


class FolderUploadViewTest(TestCase):
    """Tests for the folder upload view that preserves directory structure."""

    def setUp(self):
        self.user = User(email='victor@justice.league', is_active=True)
        self.user.set_password('b00yah_cYb0rg!')
        self.user.save(using='default')
        self.root = UserFolder.create_root_for_user(self.user, b'b00yah_cYb0rg!')
        self.client = Client()
        self.client.login(email='victor@justice.league', password='b00yah_cYb0rg!')

    def test_folder_upload_url_exists(self):
        """The folder upload URL is reachable."""
        response = self.client.get('/upload/folder/')
        # Should redirect or return 200 (GET shows the form)
        self.assertIn(response.status_code, [200, 302])

    def _post_folder_upload(self, parent_pk, filenames, contents, relative_paths):
        """Helper to POST a folder upload with proper multipart file encoding."""
        from django.test.client import encode_multipart, BOUNDARY
        data = {'parent_folder': str(parent_pk)}
        # Add relative paths
        if isinstance(relative_paths, str):
            relative_paths = [relative_paths]
        for rp in relative_paths:
            data.setdefault('relative_paths', [])
            data['relative_paths'].append(rp)
        # Build files list — test client accepts list for multi-file
        files = []
        for fname, content in zip(filenames, contents):
            files.append(SimpleUploadedFile(fname, content))
        data['folder_field'] = files if len(files) > 1 else files[0]
        return self.client.post('/upload/folder/', data)

    def test_folder_upload_creates_subfolder(self):
        """Uploading a folder creates a subfolder under the selected parent."""
        projects = UserFolder.objects.get(parent=self.root, name='projects')
        response = self._post_folder_upload(
            projects.pk,
            ['file1.txt'], [b'hello world'],
            ['my_project/file1.txt'],
        )
        # Should have created the subfolder
        self.assertTrue(
            UserFolder.objects.filter(parent=projects, name='my_project').exists()
        )

    def test_folder_upload_preserves_nested_structure(self):
        """Nested folder paths create nested UserFolder hierarchy."""
        projects = UserFolder.objects.get(parent=self.root, name='projects')
        response = self._post_folder_upload(
            projects.pk,
            ['doc.pdf', 'notes.txt'], [b'pdf content', b'note content'],
            ['alpha/docs/doc.pdf', 'alpha/notes.txt'],
        )
        # alpha folder under projects
        alpha = UserFolder.objects.filter(parent=projects, name='alpha').first()
        self.assertIsNotNone(alpha)
        # docs subfolder under alpha
        docs = UserFolder.objects.filter(parent=alpha, name='docs').first()
        self.assertIsNotNone(docs)

    def test_folder_upload_redirects_on_success(self):
        """Successful folder upload redirects to success page."""
        inbox = UserFolder.objects.get(parent=self.root, name='inbox')
        response = self._post_folder_upload(
            inbox.pk,
            ['readme.txt'], [b'read me'],
            ['stuff/readme.txt'],
        )
        self.assertEqual(response.status_code, 302)

    def test_upload_page_has_two_forms(self):
        """The upload page renders both file and folder upload forms."""
        response = self.client.get('/upload/create/')
        content = response.content.decode()
        self.assertIn('Upload File', content)
        self.assertIn('Upload Folder', content)


import json


class AjaxFileUploadTest(TestCase):
    """Tests for the single-file AJAX upload endpoint."""

    def setUp(self):
        self.user = User(email='arthur@atlantis.sea', is_active=True)
        self.user.set_password('tr1d3nt_k1ng!')
        self.user.save(using='default')
        self.root = UserFolder.create_root_for_user(self.user, b'tr1d3nt_k1ng!')
        self.client = Client()
        self.client.login(email='arthur@atlantis.sea', password='tr1d3nt_k1ng!')

    def test_ajax_file_upload_returns_json(self):
        """AJAX file upload returns JSON response."""
        inbox = UserFolder.objects.get(parent=self.root, name='inbox')
        f = SimpleUploadedFile('ocean_map.png', b'map data here')
        response = self.client.post('/upload/api/file/', {
            'file_field': f,
            'folder': inbox.pk,
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['display_name'], 'ocean_map.png')

    def test_ajax_file_upload_requires_login(self):
        """AJAX file upload rejects unauthenticated users."""
        anon = Client()
        f = SimpleUploadedFile('secret.png', b'data')
        response = anon.post('/upload/api/file/', {'file_field': f})
        self.assertIn(response.status_code, [302, 403])

    def test_ajax_file_upload_creates_one_db_record(self):
        """Each AJAX upload creates exactly one ImageFile record."""
        inbox = UserFolder.objects.get(parent=self.root, name='inbox')
        count_before = ImageFile.objects.count()
        f = SimpleUploadedFile('trident.png', b'weapon data')
        self.client.post('/upload/api/file/', {
            'file_field': f,
            'folder': inbox.pk,
        })
        self.assertEqual(ImageFile.objects.count(), count_before + 1)

    def test_ajax_file_upload_no_file_returns_error(self):
        """AJAX upload without a file returns error JSON."""
        response = self.client.post('/upload/api/file/', {})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')


class AjaxFolderFileUploadTest(TestCase):
    """Tests for the single-file AJAX folder upload endpoint."""

    def setUp(self):
        self.user = User(email='shazam@fawcett.city', is_active=True)
        self.user.set_password('sh4z4m_p0w3r!')
        self.user.save(using='default')
        self.root = UserFolder.create_root_for_user(self.user, b'sh4z4m_p0w3r!')
        self.client = Client()
        self.client.login(email='shazam@fawcett.city', password='sh4z4m_p0w3r!')

    def test_ajax_folder_file_returns_json(self):
        """AJAX folder-file upload returns JSON with status ok."""
        projects = UserFolder.objects.get(parent=self.root, name='projects')
        f = SimpleUploadedFile('readme.md', b'# Project')
        response = self.client.post('/upload/api/folder-file/', {
            'file_field': f,
            'parent_folder': projects.pk,
            'relative_path': 'my_app/readme.md',
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')

    def test_ajax_folder_file_creates_subfolder(self):
        """AJAX folder-file upload creates the subfolder from the relative path."""
        projects = UserFolder.objects.get(parent=self.root, name='projects')
        f = SimpleUploadedFile('index.html', b'<html>')
        self.client.post('/upload/api/folder-file/', {
            'file_field': f,
            'parent_folder': projects.pk,
            'relative_path': 'website/index.html',
        })
        self.assertTrue(
            UserFolder.objects.filter(parent=projects, name='website').exists()
        )

    def test_ajax_folder_file_creates_nested_folders(self):
        """AJAX folder-file creates nested folder hierarchy."""
        projects = UserFolder.objects.get(parent=self.root, name='projects')
        f = SimpleUploadedFile('deep.txt', b'deep content')
        self.client.post('/upload/api/folder-file/', {
            'file_field': f,
            'parent_folder': projects.pk,
            'relative_path': 'a/b/c/deep.txt',
        })
        a = UserFolder.objects.get(parent=projects, name='a')
        b = UserFolder.objects.get(parent=a, name='b')
        c = UserFolder.objects.get(parent=b, name='c')
        self.assertIsNotNone(c)

    def test_ajax_folder_file_rejects_other_users_parent(self):
        """Cannot upload into another user's folder."""
        other = User(email='sivana@evil.org', is_active=True)
        other.set_password('3v1l_sc13nc3!')
        other.save(using='default')
        other_root = UserFolder.create_root_for_user(other, b'3v1l_sc13nc3!')
        f = SimpleUploadedFile('steal.txt', b'mine now')
        response = self.client.post('/upload/api/folder-file/', {
            'file_field': f,
            'parent_folder': other_root.pk,
            'relative_path': 'hacked/steal.txt',
        })
        self.assertEqual(response.status_code, 403)


class UploadPageProgressBarTest(TestCase):
    """Tests that the upload page includes progress bar elements."""

    def setUp(self):
        self.user = User(email='zatanna@jla.org', is_active=True)
        self.user.set_password('cigam_sdrow!')
        self.user.save(using='default')
        UserFolder.create_root_for_user(self.user, b'cigam_sdrow!')
        self.client = Client()
        self.client.login(email='zatanna@jla.org', password='cigam_sdrow!')

    def test_upload_page_has_progress_elements(self):
        """Upload page contains progress bar markup."""
        response = self.client.get('/upload/create/')
        content = response.content.decode()
        self.assertIn('progress-bar', content)
        self.assertIn('progress-text', content)
