#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import string
import getpass
import hashlib

from tornado.ioloop import IOLoop
from tornado.web import Application, url, RequestHandler, authenticated
from tornado.options import define, options
from tornado.escape import json_encode, json_decode
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

MAX_WORKERS = 4
SECRET_LENGTH = 40


import todo_txt

define("port", default="8880", help="Worker port number")
define("config", help="Config file name", default="default_config.py")
define("todo_file", help="todo.txt file path")


def calc_hash(password, salt):
    return hashlib.sha512(password + salt).hexdigest()


def update_password(password_file, password, salt):
    password_hash = calc_hash(password, salt)
    with open(password_file, 'w') as password_fh:
        password_fh.write(password_hash)
    return password_hash


def get_secret(secret_file):
    """Return random string with length equals to SECRET_LENGTH"""
    secret_word = ''
    if os.path.exists('secret'):
        secret_word = open('secret').read().strip()
    if len(secret_word) == SECRET_LENGTH:
        return secret_word
    else:
        secret_word = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(SECRET_LENGTH))
        with open(secret_file, 'w') as secret_fh:
            secret_fh.write(secret_word)
    return secret_word


def method_proxy(f):
    @wraps(f)
    def wrapper(obj, *args, **kwargs):
        if 'method' in kwargs:
            method = kwargs.pop('method')
        else:
            method = None
        if method:
            return getattr(obj, method)(*args, **kwargs)
        else:
            return f(obj, *args, **kwargs)
    return wrapper


class RequestHandlerProxy(RequestHandler):

    def get_current_user(self):
        password_hash = self.get_secure_cookie("password_hash")
        if password_hash == self.application.password_hash:
            return password_hash
        else:
            return None

    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @method_proxy
    def get(self, *args, **kwargs):
        return super(RequestHandlerProxy, self).get(*args, **kwargs)

    @method_proxy
    def post(self, *args, **kwargs):
        return super(RequestHandlerProxy, self).post(*args, **kwargs)

    @method_proxy
    def delete(self, *args, **kwargs):
        return super(RequestHandlerProxy, self).delete(*args, **kwargs)

    @method_proxy
    def put(self, *args, **kwargs):
        return super(RequestHandlerProxy, self).put(*args, **kwargs)

    @method_proxy
    def head(self, *args, **kwargs):
        return super(RequestHandlerProxy, self).head(*args, **kwargs)

    @method_proxy
    def options(self, *args, **kwargs):
        return super(RequestHandlerProxy, self).options(*args, **kwargs)


class MainHandler(RequestHandlerProxy):

    @authenticated
    def get(self):
        self.render('main.html')


class TodoHandler(RequestHandlerProxy):

    def initialize(self):
        self.todo = todo_txt.TodoTxt(options.todo_file)

    @authenticated
    def get(self):
        result_encoded = json_encode(self.todo.serialize())
        self.write(result_encoded)

    @authenticated
    def post(self):
        todo_list = json_decode(self.request.body)
        self.todo.unserialize(todo_list)
        self.write('saved')


class LoginHandler(RequestHandlerProxy):

    def get(self):
        self.render('login.html')

    def post(self):
        password = self.request.body_arguments.get('password')[0]
        if password and self.application.is_password_valid(password):
            self.set_secure_cookie('password_hash', self.application.password_hash)
            self.redirect('/')
        else:
            self.redirect('/login')


class TodoApplication(Application):

    def __init__(self, secret_file='secret', password_file='password'):
        handlers = [
            url(r"/", MainHandler),
            url(r"/todo/", TodoHandler),
            url(r"/login", LoginHandler),
        ]
        settings = dict(
            template_path=os.path.join('static', 'html'),
            static_path=os.path.join('static'),
            debug=True,
            cookie_secret=get_secret(secret_file),
            password_file=password_file,
            login_url='/login',
        )
        super(TodoApplication, self).__init__(handlers, **settings)
        self.set_password()

    def set_password(self):
        password_file = self.settings['password_file']
        if not os.path.exists(password_file):
            password = getpass.getpass(prompt="Enter user password (it will use for login):")
            self.password_hash = update_password(
                password_file, password, self.settings['cookie_secret'])
        else:
            self.password_hash = open(self.settings['password_file']).read().strip()

    def is_password_valid(self, password):
        return self.password_hash == calc_hash(password,
                                               self.settings['cookie_secret'])


def make_app(*args, **kwargs):
    return TodoApplication(*args, **kwargs)


def start_app(app):
    app.listen(options.port)
    IOLoop.current().start()


def main():
    options.parse_command_line()
    if options.config:
        options.parse_config_file(options.config)
    app = make_app()
    start_app(app)


if __name__ == '__main__':
    main()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
