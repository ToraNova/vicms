import json, datetime
from vicore import sqlorm
from vicms.abst import BaseContent
from sqlalchemy.exc import IntegrityError

# place holder
class SQLContentMixin(sqlorm.Core):

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

class SQLContent(BaseContent):
    def __init__(self, content_class, routes_disabled = []):
        assert issubclass(content_class, SQLContentMixin)
        self._contentclass = content_class
        self.tablename = self._contentclass.__tablename__
        super().__init__(self.tablename, routes_disabled)
        self._session = None

    # DO NOT OVERRIDE
    def _find_by_id(self, id):
        return self._contentclass.query.filter(self._contentclass.id == id).first()
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
