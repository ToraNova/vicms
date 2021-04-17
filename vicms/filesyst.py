'''
a class of utility functions to handle files
'''
import os, errno, uuid
from vicms.abst import BaseContent
from flask import send_file, send_from_directory, current_app
from werkzeug.utils import secure_filename
illegal_seq =   ('*','..','&','%','$','>','<','|','!','?','`','\'','\"','=','+','@',';','{','}','#','//','\\\\',',',' ',':',';')
KBCONST = 1024
MBCONST = 1048576

class FileContent(BaseContent):

    def __init__(self, file_policy, routes_disabled = []):
        assert type(file_policy.get('dirname')) is str
        assert rdirname_allowed(file_policy['dirname']) #ensure relative directory name allowed
        self.dirname = file_policy['dirname']
        super().__init__(self.dirname, routes_disabled = routes_disabled)

        # extension checking
        if type(file_policy.get('check_extension')) is not bool:
            file_policy['check_extension'] = True
        if file_policy['check_extension']:
            assert file_policy.get('allowed_extension') is not None and type(file_policy['allowed_extension']) is list

        # mimetype checking
        if type(file_policy.get('check_mimetype')) is not bool:
            file_policy['check_mimetype'] = True
        if file_policy['check_mimetype']:
            assert file_policy.get('allowed_mimetype') is not None and type(file_policy['allowed_mimetype']) is list
            self.magic = magic.Magic(mime=True)

        if type(file_policy.get('max_filesize')) is not int:
            file_policy['max_filesize'] = 25*MBCONST # default to 25MB max size
        if file_policy['max_filesize'] < 0:
            file_policy['max_filesize'] = 0

        if type(file_policy.get('random_filename')) is not bool:
            file_policy['random_filename'] = True

        if type(file_policy.get('upload_key')) is not str:
            file_policy['upload_key'] = 'upload'
        self.fpol = file_policy

    def init_savepath(self, upload_dir):
        self.savepath = os.path.join(upload_dir, self.dirname)
        self.savepath_abs = os.path.abspath(self.savepath)
        try:
            # ensure directory exists
            os.makedirs(os.path.abspath(self.savepath))
        except OSError as e:
            if e.errno != errno.EEXIST:
                # only reraise error if it's not a "directory already exist" error
                raise

    def listdir(self):
        res = [f for f in os.listdir(self.savepath)\
                if os.path.isfile(os.path.join(self.savepath, f))]
        return res

    def download(self, filename, **kwargs):
        # see https://github.com/pallets/flask/issues/1169
        # send_from_directory prematurely aborts(404) when app.root_path not same as running dir
        #return send_from_directory(self.savepath, filename, **kwargs)
        #return send_file(os.path.join(self.savepath, filename), **kwargs)
        return send_file(os.path.join(self.savepath_abs, filename), **kwargs)

    def upload(self, fileobj, newname = None):
        # save file
        if '.' not in fileobj.filename:
            raise Exception('please ensure filename format is of \'name.extension\'.')
        fext = fileobj.filename.split('.')[-1].lower()

        if self.fpol['check_extension']:
            if fext not in self.fpol['allowed_extension']:
                raise Exception('file extension not allowed.')

        flen = get_filelen(fileobj)
        if flen > self.fpol['max_filesize'] and self.fpol['max_filesize'] > 0:
            raise Exception('file exceeded limit of %d bytes.' % self.fpol['max_filesize'])

        if self.fpol['check_mimetype']:
            mtype = self.magic.from_buffer(fileobj.stream.read(flen)) # scan mime type
            if mtype not in self.fpol['allowed_mimetype']:
                raise Exception('mimetype \'%s\' not allowed.' % mtype)
            fileobj.seek(0, 0) # seek back to beginning

        if not newname:
            if self.fpol['random_filename']:
                newname = '%s.%s' % (ensure_random_uuid(self.listdir()), fext)
            else:
                newname = fileobj.filename

        newname = secure_filename(newname)
        ffname = os.path.join(self.savepath, newname)
        if not filename_allowed(ffname):
            raise Exception("filename not allowed.")
        fileobj.save(ffname)
        return newname

    def delete(self, filename):
        ffname = os.path.join(self.savepath, filename)
        if not filename_allowed(ffname):
            raise Exception("filename not allowed.")
        try:
            os.remove(ffname)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
        return ffname

def ensure_random_uuid(existing):
    p = 10
    res = str(uuid.uuid4())
    while res in existing and p > 0:
        # keep regenerating
        res = str(uuid.uuid4())
        p -= 1
        if p < 1:
            raise Exception('uuid collision error.')
    return res

def get_filelen(fileobj):
    fileobj.seek(0, 2) # seek to end
    flen = fileobj.tell() # get size
    fileobj.seek(0, 0) # seek to beginning
    return flen

def rdirname_allowed(dirname):
    # no illegal sequences allowed
    res = True
    for s in illegal_seq:
        if s in dirname:
            res = False
    # may not be an absolute path, and prevents globbing
    return res and not dirname.startswith('/') and not dirname.endswith('/')\
            and not dirname.startswith('-')

def filename_allowed(filename):
    # no illegal sequences allowed
    res = True
    for s in illegal_seq:
        if s in filename:
            res = False
    # prevent globbing
    return res and not filename.startswith('-')
