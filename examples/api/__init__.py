'''
an absolute basic cms architecture for REST-API, with authentication
to run:
(in virtualenv @ examples/)
export FLASK_APP=api
flask run
'''
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import login_user, LoginManager, current_user, logout_user, UserMixin, login_required
from vicms.api import Content
from vicms.api.withauth import Arch, Content as AuthContent
from vicms import ContentMixin, sqlorm
# refer to examples.basic for example sqlalchemy classes
from examples.basic import PersonRecord, PairRecord, Base

class PlaceHolderAuth(UserMixin):
    is_authenticated = False

    def __init__(self):
        self.id = 1

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
    c1 = Content( PersonRecord, routes_disabled=[] )
    c2 = AuthContent( PairRecord,
            access_policy = {
                'select': None,
            },
            default_ap = login_required, routes_disabled=[]
        )

    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with vicms
    session = sqlorm.connect(app.config['DBURI'], Base)
    arch = Arch( session, [c1, c2], url_prefix = '/apitest')
    arch.init_app(app)

    lman = LoginManager()

    @lman.user_loader
    def loader(uid):
        u = PlaceHolderAuth()
        u.is_authenticated = True
        return u

    lman.init_app(app)

    @app.route('/')
    def root():
        return 'vicms-api: test app'

    # example login
    @app.route('/login/', methods=['GET'])
    def cheat():
        login_user( PlaceHolderAuth() )
        return 'logged in'

    return app
