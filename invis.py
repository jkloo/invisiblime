import os
import re

import sublime
import sublime_plugin

def is_gitignore(fname):
    return os.path.basename(fname) == '.gitignore'


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


def overwrite_ignores(data, proj_root):
    for folder in data.get('folders', []):
        ignore = find_gitignore(folder.get('path', ''), proj_root)
        if ignore:
            files, dirs = get_entries(ignore)
            idx = data['folders'].index(folder)
            data['folders'][idx]['file_exclude_patterns'] = files
            data['folders'][idx]['folder_exclude_patterns'] = dirs
    return data


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
