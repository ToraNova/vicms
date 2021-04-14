'''
TODO: This arch is WIP.
vicms-api: lightweight flexible REST-API routes for vicms.
supports multiple content per arch
'''

import json
import vicms
from flask import render_template, request, redirect, abort, flash, url_for
from sqlalchemy.exc import IntegrityError

'''
basic.Content Arch
templates: select, select_one, insert, update
content_home: redirect to content_home after insert, update, delete
set content='self' to redirect to the content's home (default behavior)
'''
class Content(vicms.BaseContent):

    def __init__(self,
            content_class,
            routes_disabled = []
        ):
        '''initialize the content structure. a content structure is used by an arch to easily create API routes
        '''
        super().__init__(content_class, routes_disabled)
        #vicms.BaseArch.__init__(self, self.tablename, {}, {}, {}, rex_callback, None)
        # api has NO templates or REROUTES. just JSON response

    def select(self):
        res = super().select()
        dar = [r.as_dict() for r in res]
        return json.dumps(dar), 200

    def select_one(self,id):
        res = super().select_one(id)
        if res is None:
            abort(404)
        return res.as_json(), 200

    def insert(self):
        if request.method != 'POST':
            abort(400)
        try:
            res = super().insert(request.form)
            return res.as_json(), 200
        except IntegrityError as e:
            return '{"err":"integrity error."}', 409
        except Exception as e:
            return '{"err":"%s"}'%(str(e)),400

    def update(self,id):
        if request.method != 'POST':
            abort(400)
        try:
            res = super().update(id, request.form)
            return res.as_json(), 200
        except IntegrityError as e:
            return '{"err":"integrity error."}', 409
        except Exception as e:
            return '{"err":"%s"}'%(str(e)),400

    def delete(self,id):
        try:
            res = super().delete(id)
            return '{"err":"none"}', 200
        except Exception as e:
            return '{"err":"%s"}'%(str(e)),400

# nothing new added, repass to allow easy importing
class Arch(vicms.Arch):
    pass
