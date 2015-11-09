# -*- coding: utf-8 -*-
"""Testing main page of application"""

import os

from tornado.options import options
from tornado.testing import AsyncHTTPTestCase

from todotxt_web import server

APP = server.make_app()
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

    # def test_todo_handler_get(self):
        # response = self.fetch('/todo/')
        # self.assertEqual(response.code, 200)
        # self.assertIn('The first task', response.body)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
