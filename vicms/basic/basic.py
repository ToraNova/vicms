'''
basic cms, custom user db, no access control
supports multiple content per arch
'''

from flask import render_template, request, redirect, abort, flash, url_for
from vicms import source, sqlorm
from sqlalchemy.exc import IntegrityError

'''
basic.ViContent Arch
templates: select, select_one, insert, update
content_home: redirect to content_home after insert, update, delete
set content='self' to redirect to the content's home (default behavior)
'''
class ViContent:

    def __init__(self, content_class,
            templates = {},
            content_home = 'vicms.select',
            content_home_kwargs = {},
            routes_disabled = []
        ):
        '''initialize the content structure. a content structure is used by an arch
        to easily create routes
        '''
        self.__templ = templates
        self.__default_tp('insert','insert.html')
        self.__default_tp('select','select.html')
        self.__default_tp('select_one','select_one.html')
        self.__default_tp('update','update.html')

        #assert issubclass(content_class, sqlorm.Base) # could be initialized from an alternative base
        assert issubclass(content_class, sqlorm.ViCMSBase)
        self.__contentclass = content_class
        self.session = None

        self.__contenthome = content_home
        if not content_home_kwargs.get('content') or content_home_kwargs.get('content') == 'self':
            content_home_kwargs['content'] = self.get_tablename()
        self.__contenthome_kwargs = content_home_kwargs
        self.__callbacks = {
                'err': lambda msg : flash(msg, 'err'),
                'ok': lambda msg : flash(msg, 'ok'),
                'warn': lambda msg : flash(msg, 'warn'),
                'ex': lambda ex : flash("an exception (%s) has occurred: %s" % (type(ex).__name__, str(ex)), 'err'),
        }

        for route in ['insert', 'select', 'select_one', 'update']:
            if route in routes_disabled:
                setattr(self, route, lambda *arg : abort(404))

    def set_callback(self, event, cbfunc):
        if not callable(cbfunc):
            raise TypeError("callback function should be callable")
        self.__callbacks[event] = cbfunc

    def callback(self, event, *args):
        return self.__callbacks[event](*args)

    # convenience functions
    def error(self, msg):
        self.callback('err', msg)

    def ok(self, msg):
        self.callback('ok', msg)

    def ex(self, e):
        self.callback('ex', e)

    def __default_tp(self, key, value):
        if not self.__templ.get(key):
            self.__templ[key] = value

    def _set_session(self, session):
        self.session = session

    def get_tablename(self):
        return self.__contentclass.__tablename__

    def __content_home(self):
        return redirect(url_for(self.__contenthome, **self.__contenthome_kwargs))

    def select(self):
        call = self.__contentclass.query.all()
        auxd = []
        for c in call:
            auxd.append(c.select_assist())
        return render_template(self.__templ['select'], data = call, auxd = auxd)

    def select_one(self,id):
        cone = self.__contentclass.query.filter(self.__contentclass.id == id).first()
        auxd = cone.select_assist()
        return render_template(self.__templ['select_one'], data = cone, auxd = auxd)

    def insert(self):
        rscode = 200
        if request.method == 'POST':
            try:
                new = self.__contentclass(request.form)
                self.session.add(new)
                self.session.commit()
                self.ok('successfully inserted')
                return self.__content_home()
            except IntegrityError as e:
                self.error('integrity error')
                rscode = 409
            except Exception as e:
                self.ex(e)
            self.session.rollback()
        form = self.__contentclass.formgen_assist(self.session)
        return render_template(self.__templ['insert'], form = form), rscode

    def update(self,id):
        rscode = 200
        targ = self.__contentclass.query.filter(self.__contentclass.id == id).first()
        if request.method == 'POST':
            try:
                targ.update(request.form)
                self.session.add(targ)
                self.session.commit()
                self.ok('successfully updated')
                return self.__content_home()
            except IntegrityError as e:
                self.error('integrity error')
                rscode = 409
            except Exception as e:
                self.ex(e)
            self.session.rollback()
        form = self.__contentclass.formgen_assist(self.session)
        return render_template(self.__templ['update'], data = targ, form = form), rscode

    def delete(self,id):
        targ = self.__contentclass.query.filter(self.__contentclass.id == id).first()
        try:
            targ.delete()
            self.session.delete(targ)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            source.eflash(e)
        return self.__content_home()

class Arch:
    def __init__(self, dburi, contents, dbase = sqlorm.Base, url_prefix = None):
        self.contents = {}
        self.__urlprefix = url_prefix
        self.session = sqlorm.connect(dburi, dbase)
        for c in contents:
            assert isinstance(c, ViContent)
            self.contents[c.get_tablename()] = c
            self.contents[c.get_tablename()]._set_session(self.session)

    def init_app(self, app):
        apparch = self.generate()
        app.register_blueprint(apparch.bp)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.session.remove()
            pass

        return app

    def generate(self):
        bp = source.make_blueprint(self.__urlprefix)

        @bp.route('/<content>/', methods=['GET'])
        def select(content):
            return self.contents[content].select()

        @bp.route('/<content>/<id>', methods=['GET'])
        def select_one(content,id):
            return self.contents[content].select_one(id)

        @bp.route('/<content>/insert', methods=['GET','POST'])
        def insert(content):
            return self.contents[content].insert()

        @bp.route('/<content>/update/<id>', methods=['GET','POST'])
        def update(content,id):
            return self.contents[content].update(id)

        @bp.route('/<content>/delete/<id>')
        def delete(content,id):
            return self.contents[content].delete(id)

        return source.AppArch(bp)
