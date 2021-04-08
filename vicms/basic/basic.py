'''
basic cms, custom user db, no access control
supports multiple content per arch
'''

from flask import render_template, request, redirect, abort, flash, url_for
from vicms import sqlorm, ViCMSMixin
from vicore import ViArchBase, AppArch
from sqlalchemy.exc import IntegrityError

cmroutes = ('select', 'select_one', 'insert', 'update', 'delete')

'''
basic.ViContent Arch
templates: select, select_one, insert, update
content_home: redirect to content_home after insert, update, delete
set content='self' to redirect to the content's home (default behavior)
'''
class ViContent(ViArchBase):

    def __init__(self, content_class,
            templates = {},
            reroutes = {},
            reroutes_kwarg = {},
            routes_disabled = []
        ):
        '''initialize the content structure. a content structure is used by an arch
        to easily create routes
        '''
        if not issubclass(content_class, ViCMSMixin):
            raise TypeError('content_class must inherit from vicms.ViCMSMixin')
        self.__contentclass = content_class
        super().__init__(self.tablename, templates, reroutes, reroutes_kwarg)
        self._reroute = self._cms_reroute # little hack to allow cms arch behavior
        self._default_tp('insert','insert.html')
        self._default_tp('select','select.html')
        self._default_tp('select_one','select_one.html')
        self._default_tp('update','update.html')

        #assert issubclass(content_class, sqlorm.Base) # could be initialized from an alternative base
        self.session = None
        self._default_rt('insert', 'vicms.select')
        self._default_rt('update', 'vicms.select')
        self._default_rt('delete', 'vicms.select')

        self.__fctab = {
                'select': self._select,
                'select_one': self._select_one,
                'insert': self._insert,
                'update': self._update,
                'delete': self._delete,
                }

        for route in cmroutes:
            if route in routes_disabled:
                self.__fctab[route] = lambda *arg : abort(404)

    @property
    def tablename(self):
        return self.__contentclass.__tablename__

    def routecall(self, route, *args):
        return self.__fctab[route](*args)

    def _set_session(self, session):
        self.session = session

    def _select(self):
        call = self.__contentclass.query.all()
        auxd = self.__contentclass.select_assist()
        return render_template(self._templ['select'], data = call, auxd = auxd)

    def _select_one(self,id):
        cone = self.__contentclass.query.filter(self.__contentclass.id == id).first()
        auxd = self.__contentclass.select_assist()
        return render_template(self._templ['select_one'], data = cone, auxd = auxd)

    def _insert(self):
        rscode = 200
        if request.method == 'POST':
            try:
                new = self.__contentclass(request.form)
                self.session.add(new)
                self.session.commit()
                self.ok('successfully inserted.')
                return self._reroute('insert')
            except IntegrityError as e:
                self.error('integrity error.')
                rscode = 409
            except Exception as e:
                self.ex(e)
            self.session.rollback()
        form = self.__contentclass.formgen_assist(self.session)
        return render_template(self._templ['insert'], form = form), rscode

    def _update(self,id):
        rscode = 200
        targ = self.__contentclass.query.filter(self.__contentclass.id == id).first()
        if request.method == 'POST':
            try:
                targ.update(request.form)
                self.session.add(targ)
                self.session.commit()
                self.ok('successfully updated.')
                return self._reroute('update')
            except IntegrityError as e:
                self.error('integrity error.')
                rscode = 409
            except Exception as e:
                self.ex(e)
            self.session.rollback()
        form = self.__contentclass.formgen_assist(self.session)
        return render_template(self._templ['update'], data = targ, form = form), rscode

    def _delete(self,id):
        targ = self.__contentclass.query.filter(self.__contentclass.id == id).first()
        try:
            targ.delete()
            self.session.delete(targ)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.ex(e)
        return self._reroute('delete')

class Arch(ViArchBase):
    def __init__(self, dburi, dbase, contents, url_prefix = None):
        super().__init__('vicms', url_prefix = url_prefix)
        self.contents = {}
        self.session = sqlorm.connect(dburi, dbase)
        for c in contents:
            assert isinstance(c, ViContent)
            self.contents[c.tablename] = c
            self.contents[c.tablename]._set_session(self.session)

    def set_session(self, session):
        for k in self.contents:
            self.contents[k]._set_session(session)

    def init_app(self, app):
        apparch = self.generate()
        app.register_blueprint(apparch.bp)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.session.remove()
            pass

        return app

    def generate(self):
        bp = self._init_bp()

        @bp.route('/<content>/', methods=['GET'])
        def select(content):
            if content not in self.contents:
                abort(404)
            return self.contents[content].routecall('select')

        @bp.route('/<content>/<id>', methods=['GET'])
        def select_one(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].routecall('select_one', id)

        @bp.route('/<content>/insert', methods=['GET','POST'])
        def insert(content):
            if content not in self.contents:
                abort(404)
            return self.contents[content].routecall('insert')

        @bp.route('/<content>/update/<id>', methods=['GET','POST'])
        def update(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].routecall('update', id)

        @bp.route('/<content>/delete/<id>')
        def delete(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].routecall('delete', id)

        return AppArch(bp)
