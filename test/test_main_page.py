# -*- coding: utf-8 -*-
"""Testing main page of application"""

import os
import unittest
import mock
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


class TestTodoTxtWebMainPage(TestHandlerBase):

    def setUp(self):
        """Fetch main page to self.page"""
        super(TestTodoTxtWebMainPage, self).setUp()
        response = self.fetch('/login', method='POST', follow_redirects=False,
                              body=urllib.urlencode({'password': PASSWORD}))
        cookies = {'Cookie': response.headers['Set-Cookie']}
        response = self.fetch('/', headers=cookies)
        self.assertEqual(response.code, 200)
        self.page = response.buffer.read()

    def test_main_page(self):
        """Test fetching main page"""
        self.assertIn('todo.txt', self.page)

    def test_includes(self):
        """Testing including js/css"""
        self.assertIn('material.min.css', self.page)
        self.assertIn('material.min.js', self.page)
        self.assertIn('icon.css', self.page)
        self.assertIn('viewport', self.page)
        self.assertIn('main.css', self.page)
        self.assertIn('jquery.js', self.page)
        self.assertIn('underscore.js', self.page)
        self.assertIn('json2.js', self.page)
        self.assertIn('backbone.js', self.page)
        self.assertIn('backbone.babysitter.js', self.page)
        self.assertIn('backbone.wreqr.js', self.page)
        self.assertIn('backbone.marionette.min.js', self.page)
        self.assertIn('todo_txt.js', self.page)


class TestTodoTxtWebLoginPage(TestHandlerBase):

    def test_login_page(self):
        """Test login functionality"""
        response = self.fetch('/')
        self.assertIn('/login', response.effective_url)
        self.assertEqual(response.code, 200)
        self.assertIn('password', response.body)

    def test_is_passwod_valid(self):
        self.assertTrue(APP.is_password_valid(PASSWORD), msg="Password is not matched")

    def test_authenticate(self):
        response = self.fetch('/login', method='POST',
                              body=urllib.urlencode({'password': PASSWORD}))
        self.assertEqual(response.code, 200)


class TestGetSecret(unittest.TestCase):

    def test_get_secret(self):
        """Test getting secret word for secure cookies"""
        self.assertTrue(server.SECRET_LENGTH)
        self.assertIsInstance(server.get_secret(SECRET_FILE), basestring)
        self.assertEqual(len(server.get_secret(SECRET_FILE)), server.SECRET_LENGTH)

    def test_app_config_login(self):
        self.assertTrue(hasattr(APP, 'settings'), msg="Application has no settings")
        self.assertEqual(APP.settings.get('cookie_secret'), server.get_secret(SECRET_FILE))
        self.assertEqual(APP.settings.get('login_url'), '/login')
        self.assertEqual(APP.settings.get('password_file'), PASSWORD_FILE)

    def test_update_password(self):
        password_hash = server.update_password(PASSWORD_FILE, PASSWORD, server.get_secret(SECRET_FILE))
        self.assertIsInstance(password_hash, basestring)
        self.assertEqual(
            password_hash, server.calc_hash(PASSWORD, server.get_secret(SECRET_FILE))
        )

    @mock.patch('getpass.getpass')
    def test_set_password(self, getpass_mock):
        getpass_mock.return_value = PASSWORD
        server.update_password(PASSWORD_FILE, PASSWORD, server.get_secret(SECRET_FILE))
        APP.set_password()
        self.assertEqual(APP.password_hash, server.calc_hash(
            PASSWORD, APP.settings.get('cookie_secret')))
        os.remove(PASSWORD_FILE)
        APP.set_password()
        self.assertTrue(getpass_mock.called)
        self.assertEqual(APP.password_hash, server.calc_hash(
            PASSWORD, APP.settings.get('cookie_secret')))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
