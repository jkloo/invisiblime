import os
from unittest.mock import Mock

try:
    import sublime
except ImportError:
    sublime = Mock()

try:
    import sublime_plugin
except ImportError:
    sublime_plugin = Mock()


from .utils import is_gitignore, find_gitignore, clean_comments, get_entries, overwrite_ignores


class UpdateIgnores(sublime_plugin.TextCommand):
    def get_project_data(self):
        return self.view.window().project_data()

    def run(self, edit, **kwargs):
        print(os.path.basename(self.view.file_name()))

    def is_enabled(self, *args):
        return is_gitignore(self.view.file_name())


class OverWriteIgnores(UpdateIgnores):
    def run(self, edit, **kwargs):
        proj_root = os.path.dirname(self.view.window().project_file_name())
        data = self.get_project_data()
        self.view.window().set_project_data(overwrite_ignores(data, proj_root))


class GitIgnoreListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if is_gitignore(view.file_name()):
            if sublime.ok_cancel_dialog('Update your sublime project data?'):
                view.run_command('over_write_ignores')
