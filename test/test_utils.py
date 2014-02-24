import os
import unittest
from unittest.mock import patch, Mock, mock_open
from io import StringIO


from ..utils import is_gitignore, find_gitignore, clean_comments, get_entries, overwrite_ignores


class TestIsGitignore(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__is_gitignore__simple(self):
        self.assertTrue(is_gitignore('.gitignore'))

    def test__is_gitignore__including_path(self):
        self.assertTrue(is_gitignore('path/.gitignore'))

    def test__is_gitignore__gitignore_dir(self):
        self.assertFalse(is_gitignore('path/.gitignore/'))

    def test__is_gitignore__gitignore_extension(self):
        self.assertFalse(is_gitignore('thing.gitignore'))


class TestFindGitignore(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('os.path.isfile', Mock(return_value=True))
    def test__find_gitignore__relative_path__isfile_true(self):
        proj_path = '/path/to/proj/root'
        p = 'rel/path'
        self.assertEqual(os.path.join(proj_path, p, '.gitignore'), find_gitignore(p, proj_path))

    @patch('os.path.isfile', Mock(return_value=True))
    def test__find_gitignore__absolute_path_isfile_true(self):
        proj_path = '/path/to/proj/root'
        p = '/abs/path'
        self.assertEqual(os.path.join(p, '.gitignore'), find_gitignore(p, proj_path))

    @patch('os.path.isfile', Mock(return_value=False))
    def test__find_gitignore__relative_path__isfile_false(self):
        proj_path = '/path/to/proj/root'
        p = 'rel/path'
        self.assertEqual(None, find_gitignore(p, proj_path))

    @patch('os.path.isfile', Mock(return_value=False))
    def test__find_gitignore__absolute_path_isfile_false(self):
        proj_path = '/path/to/proj/root'
        p = '/abs/path'
        self.assertEqual(None, find_gitignore(p, proj_path))


class TestCleanComments(unittest.TestCase):
    def test__clean_comments(self):
        test_string = 'thing1\nthing2\n# a comment\nthing3 # inline comment'
        expected = 'thing1\nthing2\nthing3'
        self.assertEqual(clean_comments(test_string), expected)


class TestGetEntries(unittest.TestCase):
    def test__get_entries__(self):
        data = 'dir1\ndir2/\n\n.file1\n*.file2\nfile3.*\n*.dir3/'
        files = ['.file1', '*.file2', 'file3.*']
        dirs = ['dir1', 'dir2', '*.dir3']
        with patch('invisiblime.utils.open', mock_open(read_data=data), create=True) as m:
            self.assertEqual(get_entries('blah'), (files, dirs))


class TestOverwriteIgnores(unittest.TestCase):
    def test__overwrite_ignores__no_folders(self):
        data = {'dat': 'data', 'ape': 2}
        proj_root = None
        self.assertEqual(data, overwrite_ignores(data, proj_root))

    @patch('invisiblime.utils.find_gitignore', Mock(return_value=True))
    @patch('invisiblime.utils.get_entries', Mock(return_value=(['thing1', 'thing2'], ['dir1', 'dir2'])))
    def test__overwrite_ignores__one_folder(self):
        data = {'dat': 'data', 'ape': 2, 'folders': [{}]}
        expected = {'dat': 'data', 'ape': 2, 'folders': [{'file_exclude_patterns': ['thing1', 'thing2'], 'folder_exclude_patterns': ['dir1', 'dir2']}]}
        self.assertEqual(overwrite_ignores(data, 'blah'), expected)

    @patch('invisiblime.utils.find_gitignore', Mock(return_value=True))
    @patch('invisiblime.utils.get_entries', Mock(return_value=(['thing1', 'thing2'], ['dir1', 'dir2'])))
    def test__overwrite_ignores__multiple_folders(self):
        data = {'dat': 'data', 'ape': 2, 'folders': [{}, {}]}
        expected = {'dat': 'data', 'ape': 2, 'folders': [{'file_exclude_patterns': ['thing1', 'thing2'], 'folder_exclude_patterns': ['dir1', 'dir2']}, {'file_exclude_patterns': ['thing1', 'thing2'], 'folder_exclude_patterns': ['dir1', 'dir2']}]}
        self.assertEqual(overwrite_ignores(data, 'blah'), expected)
