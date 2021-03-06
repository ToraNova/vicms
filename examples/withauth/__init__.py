'''
a cms arch that requires user to login before use
refer to basic examples' declarative class about PersonRecord and PairRecord
this example is initialized with a minimal login system,
do use viauth to simplify things further!
to run:
(in virtualenv @ examples/)
export FLASK_APP=basic
flask run
'''
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_login import login_user, LoginManager, current_user, logout_user, UserMixin, login_required
from vicms.basic.withauth import Arch, ViContent
from vicms import sqlorm
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from examples.basic import PersonRecord, PairRecord, Base

class PlaceHolderAuth(UserMixin):
    is_authenticated = False

    def __init__(self):
        self.id = 1

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'v3rypowerfuls3cret, or not. CHANGE THIS!@'
    app.config['DBURI'] = 'sqlite:///wlogin.db'
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

    # define a place to find the templates and the content sqlorm class
    c1 = ViContent( PersonRecord,
        # select who can access where (use of userpriv.admin_required, role_required OK!)
        access_policy = {
            'select': None,
            },
        # select the default policy, which is flask_login's login_required
        default_ap = login_required,
        templates = {
            'select':'person/select.html',
            'select_one':'person/select_one.html',
            'insert':'person/insert.html',
            'update':'person/update.html'
            }
    )
    c2 = ViContent( PairRecord,
        default_ap = login_required,
        templates = {
            'select':'pair/select.html',
            'select_one':'pair/select_one.html',
            'insert':'pair/insert.html',
            'update':'pair/update.html'
        },
    )

    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with vicms
    arch = Arch( app.config['DBURI'], Base, [c1, c2], url_prefix = '/')
    arch.init_app(app)

    # THE FOLLOWING SETUP ONLY WORKS FOR USER tester with password test123
    # do use viauth to simply following setup
    lman = LoginManager()

    @lman.user_loader
    def loader(uid):
        u = PlaceHolderAuth()
        u.is_authenticated = True
        return u

    lman.init_app(app)

    @app.route('/')
    def root():
        return render_template('home.html')

    @app.route('/login', methods=['GET','POST'])
    def login():
        if request.method == 'POST':
            if request.form.get('username') == 'tester' and request.form.get('password') == 'test123':
                login_user( PlaceHolderAuth() )
                return redirect(url_for('vicms.select', content='pairrec'))
        return 'please POST to login'

    @app.route('/logout')
    def logout():
        logout_user()
        return 'logged out'

    return app
