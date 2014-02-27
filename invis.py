import os
from unittest.mock import MagicMock

try:
    import sublime
except ImportError:
    sublime = MagicMock()

try:
    import sublime_plugin
except ImportError:
    sublime_plugin = MagicMock()


from .utils import is_gitignore, find_gitignore, clean_comments, get_entries, overwrite_ignores


class UpdateIgnores(sublime_plugin.TextCommand):

    def get_project_data(self):
        return self.view.window().project_data()

    def run(self, edit, **kwargs):
        print(os.path.basename(self.view.file_name()))

    def is_enabled(self, *args):
        return is_gitignore(self.view.file_name())


class OverwriteIgnores(UpdateIgnores):
    def run(self, edit, **kwargs):
        proj_root = os.path.dirname(self.view.window().project_file_name())
        data = self.get_project_data()
        self.view.window().set_project_data(overwrite_ignores(data, proj_root))


class GitIgnoreListener(sublime_plugin.EventListener):
    strat_descriptions = [['overwrite', 'Overwrite my currently ignored files and directories.'],
                          ['none', 'Don\'t try to help me; I don\'t need you.']]
    strategies = {'overwrite': 'overwrite_ignores'}

    def call(self, index):
        item = self.strat_descriptions[index][0]
        self.view.run_command(self.strategies.get(item, ''))

    def on_post_save(self, view):
        if is_gitignore(view.file_name()):
            self.view = view
            settings = sublime.load_settings('Invisiblime.sublime-settings')
            strat = settings.get('strategy', '')
            flattened = [x[0] for x in self.strat_descriptions]
            if strat in flattened:
                self.call(flattened.index(strat))
            else:
                view.window().show_quick_panel(self.strat_descriptions, self.call)
