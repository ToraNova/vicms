'''
basic cms, custom user db, no access control
supports multiple content per arch
'''

import vicms
from flask import render_template, request, redirect, abort, flash, url_for
from sqlalchemy.exc import IntegrityError

class FileContent(vicms.BaseArch, vicms.FileContent):
    def __init__(self,
            file_policy,
            templates = {},
            reroutes = {},
            reroutes_kwarg = {},
            rex_callback = {},
            routes_disabled = []
        ):

        vicms.FileContent.__init__(self, file_policy, routes_disabled)
        vicms.BaseArch.__init__(self, self.dirname, templates, reroutes, reroutes_kwarg, rex_callback, None)

        self._default_tp('insert','upload.html')
        self._default_tp('select','dirlist.html')
        self._default_tp('select_one','preview.html')

        self._default_rt('insert', 'vicms.select')
        self._default_rt('delete', 'vicms.select')
        # add in 'additional' reroute arg 'content', pass in dirname/relative save path
        self._reroute_mod('content',self.dirname)

    def select(self):
        res = super().listdir()
        return render_template(self._templ['select'], data = res)

    def select_one(self,filename):
        return super().download(filename)

    def insert(self):
        if request.method == 'POST':
            try:
                ufile = request.files.get(self.fpol['upload_key'])
                res = super().upload(ufile)
                self.ok('insert', 'successfully uploaded.')
                return self._reroute('insert', filename=res)
            except Exception as e:
                self.ex('insert', e)
        return render_template(self._templ['insert'])

    def update(self,filename):
        return 'not implemented on basic/FileContent.'

    def delete(self,filename):
        res = 'nofile'
        try:
            res = super().delete(filename)
            self.ok('delete', 'successfully deleted.')
        except Exception as e:
            self.ex('delete', e)
        return self._reroute('delete', filename=res)


'''
basic.SQLContent Arch
templates: select, select_one, insert, update
content_home: redirect to content_home after insert, update, delete
set content='self' to redirect to the content's home (default behavior)
'''
class SQLContent(vicms.BaseArch, vicms.SQLContent):

    def __init__(self,
            content_class,
            templates = {},
            reroutes = {},
            reroutes_kwarg = {},
            rex_callback = {},
            routes_disabled = []
        ):
        '''initialize the content structure. a content structure is used by an arch
        to easily create routes
        '''
        # explicit constructor calls
        vicms.SQLContent.__init__(self, content_class, routes_disabled)
        vicms.BaseArch.__init__(self, self.tablename, templates, reroutes, reroutes_kwarg, rex_callback, None)

        #self._reroute = self._cms_reroute # little hack to allow cms arch behavior
        self._default_tp('insert','insert.html')
        self._default_tp('select','select.html')
        self._default_tp('select_one','select_one.html')
        self._default_tp('update','update.html')

        self._default_rt('insert', 'vicms.select')
        self._default_rt('update', 'vicms.select')
        self._default_rt('delete', 'vicms.select')
        # add in 'additional' reroute arg 'content', pass in tablename
        self._reroute_mod('content',self.tablename)

    def select(self):
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
                return self._reroute('insert', id=res.id)
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
                return self._reroute('update', id=res.id)
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
        return self._reroute('delete', id=targ.id)

# this is roughly the same as vicms arch, didn't add anything new, just to simplify imports
class Arch(vicms.Arch):
    pass
