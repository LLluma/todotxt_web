# -*- coding: utf-8 -*-
"""Testing main page of application"""

import os
import urllib

from tornado.options import options
from tornado.testing import AsyncHTTPTestCase

from todotxt_web import server

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
        with open(options.todo_file, 'w') as todo_fh:
            todo_fh.write('The first task\n')
            todo_fh.write('The second task\n')
            todo_fh.write('Yet another task\n')

    def tearDown(self):
        if os.path.exists(options.todo_file):
            os.remove(options.todo_file)

    def test_todo_handler_get(self):
        response = self.fetch('/login', method='POST', follow_redirects=False,
                              body=urllib.urlencode({'password': PASSWORD}))
        cookies = {'Cookie': response.headers['Set-Cookie']}
        response = self.fetch('/todo/', headers=cookies)
        self.assertEqual(response.code, 200)
        self.assertIn('The first task', response.body)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
