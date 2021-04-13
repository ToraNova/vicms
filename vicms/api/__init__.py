'''
TODO: This arch is WIP.
vicms-api: lightweight flexible REST-API routes for vicms.
supports multiple content per arch
'''

import vicms
from flask import render_template, request, redirect, abort, flash, url_for
from sqlalchemy.exc import IntegrityError

'''
basic.Content Arch
templates: select, select_one, insert, update
content_home: redirect to content_home after insert, update, delete
set content='self' to redirect to the content's home (default behavior)
'''
class Content(vicms.BaseContent, vicms.BaseArch):

    def __init__(self,
            content_class,
            rex_callback = {},
            routes_disabled = []
        ):
        '''initialize the content structure. a content structure is used by an arch
        to easily create routes
        '''
        # explicit constructor calls
        vicms.BaseContent.__init__(self, content_class, routes_disabled)
        vicms.BaseArch.__init__(self, self.tablename, {}, {}, {}, rex_callback, None)
        # api has NO templates or REROUTES. just JSON response

    def select(self):
        # TODO: render a json object
        res = super().select()
        return render_template(self._templ['select'], data = res)

    def select_one(self,id):
        res = super().select_one(id)
        return render_template(self._templ['select_one'], data = res)

    def insert(self):
        rscode = 200
        if request.method == 'POST':
            try:
                res = super().insert(request.form)
                self.ok('insert', 'successfully inserted.')
                return self._reroute('insert')
            except IntegrityError as e:
                self.err('insert', 'integrity error.')
                rscode = 409
            except Exception as e:
                self.ex('insert', e)
        fauxd = self.fauxd_generate()
        return render_template(self._templ['insert'], form_auxd = fauxd), rscode

    def update(self,id):
        rscode = 200
        targ = self._contentclass.query.filter(self._contentclass.id == id).first()
        if request.method == 'POST':
            try:
                res = super().update(id, request.form)
                self.ok('update', 'successfully updated.')
                return self._reroute('update')
            except IntegrityError as e:
                self.err('update', 'integrity error.')
                rscode = 409
            except Exception as e:
                self.ex('update', e)
        fauxd = self.fauxd_generate()
        return render_template(self._templ['update'], data = targ, form_auxd = fauxd), rscode

    def delete(self,id):
        targ = self._contentclass.query.filter(self._contentclass.id == id).first()
        try:
            res = super().delete(id)
            self.ok('delete', 'successfully deleted.')
        except Exception as e:
            self.ex('delete', e)
        return self._reroute('delete')

# nothing new added, repass to allow easy importing
class Arch(vicms.Arch):
    pass
