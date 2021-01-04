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
            **content_home_kwargs
        ):
        '''initialize the content structure. a content structure is used by an arch
        to easily create routes
        '''
        self.__templ = templates
        self.__default_tp('insert','insert.html')
        self.__default_tp('select','select.html')
        self.__default_tp('select_one','select_one.html')
        self.__default_tp('update','update.html')

        assert issubclass(content_class, sqlorm.Base)
        self.__contentclass = content_class
        self.session = None

        self.__contenthome = content_home
        if not content_home_kwargs.get('content') or content_home_kwargs.get('content') == 'self':
            content_home_kwargs['content'] = self.get_tablename()
        self.__contenthome_kwargs = content_home_kwargs

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
        if request.method == 'POST':
            try:
                new = self.__contentclass(request.form)
                self.session.add(new)
                self.session.commit()
                source.sflash('successfully inserted')
                return self.__content_home()
            except IntegrityError as e:
                self.session.rollback()
                source.emflash('integrity error')
            except Exception as e:
                self.session.rollback()
                source.eflash(e)
        form = self.__contentclass.formgen_assist(self.session)
        return render_template(self.__templ['insert'], form = form)

    def update(self,id):
        targ = self.__contentclass.query.filter(self.__contentclass.id == id).first()
        if request.method == 'POST':
            try:
                targ.update(request.form)
                self.session.add(targ)
                self.session.commit()
                source.sflash('successfully updated')
                return self.__content_home()
            except IntegrityError as e:
                self.session.rollback()
                source.emflash('integrity error')
            except Exception as e:
                self.session.rollback()
                source.eflash(e)
        form = self.__contentclass.formgen_assist(self.session)
        return render_template(self.__templ['update'], data = targ, form = form)

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
    def __init__(self, dburi, contents, url_prefix = None):
        self.contents = {}
        self.__urlprefix = url_prefix
        self.session = sqlorm.connect(dburi)
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
