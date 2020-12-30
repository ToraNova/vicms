'''
basic authentication (username, password)
no database systems, users defined by python scripts
'''

from flask import render_template, request, redirect, abort, flash, url_for
from vicms import source, sqlorm

class Arch:
    def __init__(self, dburi, content_class,
            templates = {
                'select':'select.html',
                'select_one':'select_one.html',
                'insert':'insert.html',
                'update':'update.html'
            },
            reroutes = {
                'insert':'select',
                'update':'select',
                'delete':'select'
            },
            url_prefix = None
        ):
        '''
        initialize the architecture for the vial
        templ is a dictionary that returns user specified templates to user on given routes
        reroutes is a dictionary that reroutes the user after certain actions on given routes
        '''
        self.__templ = templates
        self.__route = reroutes
        self.__urlprefix = url_prefix
        assert issubclass(content_class, sqlorm.Base)
        self.__contentclass = content_class
        self.session = sqlorm.connect(dburi)

    def __urlstrgen(self, tstr):
        return '%s.%s' % (self.__contentclass.__tablename__,tstr)

    def init_app(self, app):
        apparch = self.generate()
        app.register_blueprint(apparch.bp)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.session.remove()
            pass

        return app

    def generate(self):
        bp = source.make_blueprint(self.__contentclass.__tablename__, self.__urlprefix)

        @bp.route('/select', methods=['GET'])
        def select():
            call = self.__contentclass.query.all()
            return render_template(self.__templ['select'], data = call)

        @bp.route('/select/<id>', methods=['GET'])
        def select_one(id):
            cone = self.__contentclass.query.filter(self.__contentclass.id == id).first()
            return render_template(self.__templ['select_one'], data = cone)

        @bp.route('/insert', methods=['GET','POST'])
        def insert():
            if request.method == 'POST':
                try:
                    new = self.__contentclass(request.form)
                    self.session.add(new)
                    self.session.commit()
                    source.sflash('successfully inserted')
                    return redirect(url_for(self.__urlstrgen(self.__route['insert'])))
                except Exception as e:
                    self.session.rollback()
                    source.eflash(e)
            return render_template(self.__templ['insert'])

        @bp.route('/update/<id>', methods=['GET','POST'])
        def update(id):
            targ = self.__contentclass.query.filter(self.__contentclass.id == id).first()
            if request.method == 'POST':
                try:
                    targ.update(request.form)
                    self.session.add(targ)
                    self.session.commit()
                    return redirect(url_for(self.__urlstrgen(self.__route['update'])))
                except Exception as e:
                    self.session.rollback()
                    source.eflash(e)
            return render_template(self.__templ['update'], data = targ)

        @bp.route('/delete/<id>')
        def delete(id):
            targ = self.__contentclass.query.filter(self.__contentclass.id == id).first()
            try:
                targ.delete()
                self.session.delete(targ)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                source.eflash(e)
            return redirect(url_for(self.__urlstrgen(self.__route['delete'])))

        return source.AppArch(bp)
