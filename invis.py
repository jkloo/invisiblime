import os
import re

import sublime
import sublime_plugin


def find_gitignore(path, proj_root):
    p = os.path.join(proj_root, path, '.gitignore')
    if os.path.isfile(p):
        return p
    else:
        return None


def clean_comments(text):
    """ remove #-style comments from some text. """
    return re.sub(r'\s*#.*', '', text)


def get_entries(fname):
    file_patterns = []
    dir_patterns = []
    with open(fname, 'r') as f:
        for l in clean_comments(f.read()).split('\n'):
            l = l.strip()
            if not l:
                continue
            elif l[-1] == '/' or '.' not in l:
                dir_patterns.append(l.rstrip('/'))
            elif l:
                file_patterns.append(l)
    return file_patterns, dir_patterns


class UpdateIgnores(sublime_plugin.TextCommand):
    def get_project_settings(self):
        return self.view.window().project_data()

    def get_git_ignores(self):
        folders = self.get_project_settings().get('folders', [])

    def run(self, edit, **kwargs):
        print(os.path.basename(self.view.file_name()))

    def is_enabled(self, *args):
        return os.path.basename(self.view.file_name()) == '.gitignore'


class OverWriteIgnores(UpdateIgnores):
    def run(self, edit, **kwargs):
        proj_root = os.path.dirname(self.view.window().project_file_name())
        settings = self.get_project_settings()
        for folder in settings.get('folders', []):
            ignore = find_gitignore(folder.get('path', ''), proj_root)
            if ignore:
                files, dirs = get_entries(ignore)
                idx = settings['folders'].index(folder)
                settings['folders'][idx]['file_exclude_patterns'] = files
                settings['folders'][idx]['folder_exclude_patterns'] = dirs

        self.view.window().set_project_data(settings)


class GitIgnoreListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if os.path.basename(view.file_name()) == '.gitignore':
            if sublime.ok_cancel_dialog('Update your sublime project settings?'):
                view.run_command('over_write_ignores')
