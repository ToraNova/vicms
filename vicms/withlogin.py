'''
basic cms, custom user db with routes requiring login
used with flask-login
this can be used with viauth
supports multiple content per arch
'''

from flask import render_template, request, redirect, abort, flash, url_for
from vicms import source, sqlorm, basic
from flask_login import current_user, login_required

class Arch(basic.Arch):
    def __init__(self, dburi, contents, url_prefix = None):
        super().__init__(dburi, contents, url_prefix)

    def generate(self):
        bp = source.make_blueprint(self.__urlprefix)

        @bp.route('/<content>/', methods=['GET'])
        @login_required
        def select(content):
            return self.contents[content].select()

        @bp.route('/<content>/<id>', methods=['GET'])
        @login_required
        def select_one(content,id):
            return self.contents[content].select_one(id)

        @bp.route('/<content>/insert', methods=['GET','POST'])
        @login_required
        def insert(content):
            return self.contents[content].insert()

        @bp.route('/<content>/update/<id>', methods=['GET','POST'])
        @login_required
        def update(content,id):
            return self.contents[content].update(id)

        @bp.route('/<content>/delete/<id>')
        @login_required
        def delete(content,id):
            return self.contents[content].delete(id)

        return source.AppArch(bp)
