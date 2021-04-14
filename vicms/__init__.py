import json, datetime
from flask import abort
from vicore import BaseArch, sqlorm
from sqlalchemy.exc import IntegrityError

cmroutes = ('select', 'select_one', 'insert', 'update', 'delete')

# place holder
class ContentMixin(sqlorm.Core):

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_dict(self):
        # dump all table into a dictionary
        od = {c.name: (getattr(self, c.name)) for c in self.__table__.columns}

        for k,v in od.items():
            # convert dates to isoformat
            if type(v) is datetime.datetime:
                od[k] = v.isoformat()
        return od

    def form_auxdata_generate(session):
        return []

    def update(self, reqform):
        pass

    def delete(self):
        pass

class BaseContent:
    def __init__(self, content_class, routes_disabled = []):
        assert issubclass(content_class, ContentMixin)
        self._contentclass = content_class
        self._session = None

        for route in cmroutes:
            if route in routes_disabled:
                setattr(self, route, lambda *arg : abort(404))

    # DO NOT OVERRIDE
    def _find_by_id(self, id):
        return self._contentclass.query.filter(self._contentclass.id == id).first()
    @property
    def tablename(self):
        return self._contentclass.__tablename__
    def fauxd_generate(self):
        return self._contentclass.form_auxdata_generate(self._session)
    def set_session(self, session):
        self._session = session

    def select(self):
        return self._contentclass.query.all()

    def select_one(self, id):
        return self._find_by_id(id)

    def insert(self, reqform):
        try:
            tar = self._contentclass(reqform)
            self._session.add(tar)
            self._session.commit()
            return tar
        except Exception as e:
            self._session.rollback()
            raise e

    def update(self, id, reqform):
        try:
            tar = self._find_by_id(id)
            tar.update(reqform)
            self._session.add(tar)
            self._session.commit()
            return tar
        except Exception as e:
            self._session.rollback()
            raise e

    def delete(self, id):
        try:
            tar = self._find_by_id(id)
            tar.delete()
            self._session.delete(tar)
            self._session.commit()
            return tar
        except Exception as e:
            self._session.rollback()
            raise e

class Arch(BaseArch):
    def __init__(self, sqlorm_session, contents, url_prefix = None):
        super().__init__('vicms', url_prefix = url_prefix)
        self.contents = {}
        self._session = sqlorm_session
        for c in contents:
            assert isinstance(c, BaseContent)
            self.contents[c.tablename] = c
            self.contents[c.tablename].set_session(self._session)

    def set_session(self, session):
        for k in self.contents:
            self.contents[k].set_session(session)

    def init_app(self, app):
        bp = self.generate_blueprint()
        app.register_blueprint(bp)

        # teardown context for the sqlorm session
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self._session.remove()

        return app

    def generate_blueprint(self):
        bp = self._init_bp()

        @bp.route('/<content>/', methods=['GET'])
        def select(content):
            if content not in self.contents:
                abort(404)
            return self.contents[content].select()

        @bp.route('/<content>/<id>', methods=['GET'])
        def select_one(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].select_one(id)

        @bp.route('/<content>/insert', methods=['GET','POST'])
        def insert(content):
            if content not in self.contents:
                abort(404)
            return self.contents[content].insert()

        @bp.route('/<content>/update/<id>', methods=['GET','POST'])
        def update(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].update(id)

        @bp.route('/<content>/delete/<id>')
        def delete(content,id):
            if content not in self.contents:
                abort(404)
            return self.contents[content].delete(id)

        return bp
