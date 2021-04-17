from flask import abort
from vicore import BaseArch, sqlorm
from vicms.abst import BaseContent
from vicms.database import SQLContentMixin, SQLContent
from vicms.filesyst import FileContent
cmroutes = ('select', 'select_one', 'insert', 'update', 'delete')

# late-binding vs. early binding
# https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
def route_rewrap(wrap, routef):
    @wrap
    def f(*args):
        return routef(*args)
    return f

'''
main architectural class
'''
class Arch(BaseArch):
    def __init__(self, contents, sqlorm_session = None, url_prefix = None):
        super().__init__('vicms', url_prefix = url_prefix)
        self.contents = {}
        self._session = sqlorm_session
        for c in contents:
            assert isinstance(c, BaseContent)
            self.contents[c.content_name] = c
        self.set_session(self._session)

    def set_session(self, session):
        if self._session:
            for k in self.contents:
                if isinstance(self.contents[k], SQLContent):
                    self.contents[k].set_session(self._session)

    def init_app(self, app):
        bp = self.generate_blueprint()
        app.register_blueprint(bp)

        for k in self.contents:
            if isinstance(self.contents[k], FileContent):
                assert type(app.config.get('UPLOAD_FOLDER')) is str
                self.contents[k].init_savepath(app.config['UPLOAD_FOLDER'])

        if self._session:
            # teardown context for the sqlorm session, if session is present
            @app.teardown_appcontext
            def shutdown_session(exception=None):
                self._session.remove()
        return app

    def generate_blueprint(self):
        bp = self._init_bp()

        @bp.route('/<path:content>/', methods=['GET'])
        def select(content):
            if content not in self.contents:
                abort(404)
            return self.contents[content].select()

        @bp.route('/<path:content>/<string:id>', methods=['GET'])
        def select_one(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].select_one(id)

        @bp.route('/<path:content>/insert', methods=['GET','POST'])
        def insert(content):
            if content not in self.contents:
                abort(404)
            return self.contents[content].insert()

        @bp.route('/<path:content>/update/<string:id>', methods=['GET','POST'])
        def update(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].update(id)

        @bp.route('/<path:content>/delete/<string:id>')
        def delete(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].delete(id)

        return bp
