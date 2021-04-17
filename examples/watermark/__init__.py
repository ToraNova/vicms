import os
from vicms.basic import Arch, FileContent
from flask import Flask, render_template, redirect, url_for, flash, request

_path_ = os.path.realpath(__file__)
_base_, _file_ = os.path.split(_path_)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    #app.config['DBURI'] = 'sqlite:///basic.db' # don't really need this, coz no database
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # MAX MAX_CONTENT_LENGTH at 50 MB
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(_base_), 'uploads')
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    c = FileContent(
                {
                'dirname': 'watermark',
                'check_extension' : True,
                'check_mimetype' : False,
                'allowed_extension' : ['jpg','png','jpeg'],
                'max_filesize' : app.config['MAX_CONTENT_LENGTH'], # 50MB
                'random_filename' : True,
                'upload_key' : 'ufile', # the label on the HTML form
                },
            templates= { 'insert':'watermark_upload.html', },
            reroutes= {'insert': 'watermark'}, # redirect to watermark function
            reroutes_kwarg = { 'insert': {'filename':None} }, # passthrough filename
            )

    arch = Arch( [c], url_prefix = None)
    arch.init_app(app)

    @app.route('/')
    def root():
        return render_template('index.html')

    @app.route('/edit/<path:filename>', methods=['GET', 'POST'])
    def watermark(filename):
        if request.method == 'POST':
            return 'ok'
        else:
            return render_template('watermark_exec.html', filename=filename)

    return app
