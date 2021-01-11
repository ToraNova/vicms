'''
basic cms, custom user db with routes requiring login
used with flask-login
this can be used with viauth
supports multiple content per arch
'''
from flask import render_template, request, redirect, abort, flash, url_for
from vicms import source, sqlorm
from vicms.basic import basic
from flask_login import current_user, login_required

class ViContent(basic.ViContent):

    @login_required
    def __select(self):
        return super().select()

    @login_required
    def __select_one(self, id):
        return super().select_one(id)

    @login_required
    def __insert(self):
        return super().insert()

    @login_required
    def __update(self, id):
        return super().update(id)

    @login_required
    def __delete(self, id):
        return super().delete(id)

    def __init__(self, content_class,
            login_not_required = [],
            templates = {},
            content_home = 'vicms.select',
            content_home_kwargs = {},
            routes_disabled = []
        ):
        super().__init__(content_class, templates, content_home, content_home_kwargs, routes_disabled)

        # set login_required paths
        for k in ['select', 'select_one', 'insert', 'update', 'delete']:
            if k not in login_not_required:
                setattr(self, k, getattr(self, '_ViContent__'+k))

class Arch(basic.Arch):
    def __init__(self, dburi, contents, dbase = sqlorm.Base, url_prefix = None):
        super().__init__(dburi, contents, dbase, url_prefix)

    def generate(self):
        return super().generate()
