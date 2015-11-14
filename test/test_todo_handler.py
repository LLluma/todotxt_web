# -*- coding: utf-8 -*-
"""Testing main page of application"""

import os
import urllib

from tornado.options import options
from tornado.testing import AsyncHTTPTestCase
from tornado.escape import json_encode, json_decode

from todotxt_web import server
from todotxt_web import todo_txt

SECRET_FILE = 'test/secret'
PASSWORD_FILE = 'test/password'
PASSWORD = "Hello world"

server.update_password(PASSWORD_FILE, PASSWORD, server.get_secret(SECRET_FILE))

APP = server.make_app(secret_file=SECRET_FILE, password_file=PASSWORD_FILE)
options.parse_config_file(os.path.join('test', 'config.py'))


class TestHandlerBase(AsyncHTTPTestCase):
    """TestCase with initialized app"""

    def get_app(self):
        return APP      # this is the global app that we created above.


class TestTodoHandler(TestHandlerBase):

    def setUp(self):
        super(TestTodoHandler, self).setUp()
        self.todo = todo_txt.TodoTxt(options.todo_file)
        self.todo.add('The first task')
        self.todo.add('The second task')
        self.todo.add('Yet another task')

    def tearDown(self):
        if os.path.exists(options.todo_file):
            os.remove(options.todo_file)
        if os.path.exists(self.todo.done_txt.file_name):
            os.remove(self.todo.done_txt.file_name)

    def get_login_cookies(self):
        response = self.fetch('/login', method='POST', follow_redirects=False,
                              body=urllib.urlencode({'password': PASSWORD}))
        cookies = {'Cookie': response.headers['Set-Cookie']}
        return cookies

    def test_todo_handler_get(self):
        cookies = self.get_login_cookies()
        response = self.fetch('/todo/', headers=cookies)
        self.assertEqual(response.code, 200)
        self.assertIn('The first task', response.body)

    def test_todo_archive(self):
        cookies = self.get_login_cookies()
        archive_data = [
            {'done': False, 'line': "Not done task 1"},
            {'done': True, 'line': "Done task 1"},
            {'done': False, 'line': "Not done task 2"},
            {'done': True, 'line': "Done task 2"},
        ]
        response = self.fetch('/todo/archive', method='POST',
                              headers=cookies, body=json_encode(archive_data))
        self.assertEqual(response.code, 200)
        result_list = json_decode(response.body)
        self.assertEqual(len(result_list), 2, msg="Todo is not archived")
        self.assertIn("x Done task 1", self.todo.done_txt)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
