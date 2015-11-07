# -*- coding: utf-8 -*-
import os
import shutil
from contextlib import contextmanager

BACKUP_EXT = '.bkp'


class TodoTxt(object):
    """Wrapper Class for manipulating todo.txt"""

    def __init__(self, file_name):
        self.file_name = file_name
        if not os.path.exists(file_name):
            open(file_name, 'a').close()

    def add(self, record):
        """Adding new record to todo.txt"""
        if not record.endswith("\n"):
            record += "\n"
        with open(self.file_name, 'a') as todo_fh:
            todo_fh.write(record)

    @contextmanager
    def _get_handlers(self):
        """Make backup of todo.txt and return two file handlers:
        todo.txt -- in write mode and todo.txt.bkp -- in read mode.
        """
        try:
            shutil.copy(self.file_name, self.file_name + BACKUP_EXT)
            todo_fh = open(self.file_name, 'wb')
            backup_fh = open(self.file_name + BACKUP_EXT)
            yield todo_fh, backup_fh
        finally:
            todo_fh.close()
            backup_fh.close()

    def done(self, record):
        """Mark record as done prepend 'x' to start of line"""
        if not record.endswith("\n"):
            record += "\n"
        with self._get_handlers() as (todo_fh, backup_fh):
            for line in backup_fh:
                if line == record:
                    line = 'x ' + line
                todo_fh.write(line)

    def clean(self):
        """Remove all records which are marked as done"""
        with self._get_handlers() as (todo_fh, backup_fh):
            for line in backup_fh:
                if line.startswith('x '):
                    continue
                todo_fh.write(line)

    def __iter__(self):
        with open(self.file_name) as todo_fh:
            for line in todo_fh:
                yield line

    @staticmethod
    def serialize_line(line):
        """Converting text line to representing dictionary"""
        result = {'projects': [], 'contexts': [], 'done': False}
        line = line.strip()
        if line.startswith('x '):
            line = line[2:].strip()
            result['done'] = True
        words = []
        for word in line.split(' '):
            if not word:
                continue
            if word.startswith('+'):
                result['projects'].append(word)
                continue
            if word.startswith('@'):
                result['contexts'].append(word)
                continue
            words.append(word)
        result.update({'line': " ".join(words)})
        return result

    def serialize(self):
        """Return serialized todo
        Method returns list of dictionaries which represent todo list
        """
        result = []
        for line in self:
            result.append(self.serialize_line(line))
        return result

    @staticmethod
    def unserialize_line(line_dict):
        """Convert representing dictionary to text line"""
        result = ''
        if line_dict.get('done'):
            result += 'x '
        result += line_dict.get('line', '')
        for project in line_dict.get('projects', []):
            result += ' ' + project
        for context in line_dict.get('contexts', []):
            result += ' ' + context
        return result

    def unserialize(self, todo_list):
        """Convert representing list of dictionary to text and save"""
        with self._get_handlers() as (todo_fh, backup_fh):
            for line_dict in todo_list:
                todo_fh.write(self.unserialize_line(line_dict).encode('UTF-8') + "\n")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
