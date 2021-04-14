'''
an absolute basic cms architecture for REST-API
to run:
(in virtualenv @ examples/)
export FLASK_APP=basic
flask run
'''
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from vicms.api import Arch, Content
from vicms import ContentMixin, sqlorm
# refer to examples.basic for example sqlalchemy classes
from examples.basic import PersonRecord, PairRecord, Base

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///basic.db'
    app.testing = False
    if test_config:
        app.config.from_mapping(test_config)

    # create table
    try:
        PersonRecord.create_table(app.config['DBURI'])
        PairRecord.create_table(app.config['DBURI'])
    except Exception as e:
        # ignore if table already exist
        #print(e)
        pass

    # the api class is pretty simple, just specify the content_class (and if any, routes_disabled)
    c1 = Content(PersonRecord, routes_disabled=[])
    c2 = Content(PairRecord, routes_disabled=[])

    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with vicms
    session = sqlorm.connect(app.config['DBURI'], Base)
    arch = Arch( session, [c1, c2], url_prefix = '/apitest')
    arch.init_app(app)

    @app.route('/')
    def root():
        return 'vicms-api: test app'

    return app
