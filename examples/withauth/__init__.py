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
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_user, LoginManager, current_user, logout_user, UserMixin, login_required
from vicms import SQLContentMixin, sqlorm
from vicms.basic.withauth import Arch, SQLContent
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# users declare their own declarative Base, or use ones that are provided by other libs
# i.e., 's sqlorm.Base
Base = declarative_base()

class PersonRecord(SQLContentMixin, Base):
    '''an example content class that can be used by the cms library'''
    __tablename__ = "personrec"
    id = Column(Integer, primary_key = True)
    name = Column(String(50),unique=True,nullable=False)
    birthdate = Column(DateTime(),unique=False, nullable=True)

    def strdate(self):
        return '' if not self.birthdate else self.birthdate.strftime("%Y-%m-%d")

    # this is called on insertion GETs, a variable form_data is returned to jinja to help
    # dynamic form creation (if necessary, can be left out)
    # the variable passed to html/jinja is form_auxd
    def form_auxdata_generate(session):
        return []

    # this is called on insertion, decide what to insert and how based on form
    # this is in a try-catch block, raise an exception to abort if necessary
    def __init__(self, reqform):
        self.update(reqform)

    # this is called on update, decide what to change and how based on form
    # this is in a try-catch block, raise an exception to abort if necessary
    def update(self, reqform):
        self.name = reqform.get("name")
        self.birthdate = datetime.strptime(reqform.get("birthdate"),"%Y-%m-%d")

    # this is called before deletion
    # this is in a try-catch block, raise an exception to abort if necessary
    def delete(self):
        pass

class PairRecord(SQLContentMixin, Base):
    __tablename__ = "pairrec"
    id = Column(Integer, primary_key = True)
    aid = Column(Integer, ForeignKey('personrec.id'), nullable=True)
    bid = Column(Integer, ForeignKey('personrec.id'), nullable=True)
    aperson = relationship("PersonRecord", foreign_keys=[aid])
    bperson = relationship("PersonRecord", foreign_keys=[bid])

    # this is called on insertion GETs, a variable form_data is returned to jinja to help
    # dynamic form creation (if necessary, can be left out)
    # the variable passed to html/jinja is form_auxd
    def form_auxdata_generate(session):
        p = PersonRecord.query.all()
        return p if p else []

    # this is called on insertion, decide what to insert and how based on form
    # this is in a try-catch block, raise an exception to abort if necessary
    def __init__(self, reqform):
        self.update(reqform)

    # this is called on update, decide what to change and how based on form
    # this is in a try-catch block, raise an exception to abort if necessary
    def update(self, reqform):
        self.aid = reqform.get("aid")
        self.bid = reqform.get("bid")
        if(self.aid == self.bid):
            raise Exception("a person may not pair with themself")

    # this is called before deletion
    # this is in a try-catch block, raise an exception to abort if necessary
    def delete(self):
        pass

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
    c1 = SQLContent( PersonRecord,
        # select who can access where (use of userpriv.admin_required, role_required OK!)
        # set to None to allow anyone to access (public, no access policy)
        access_policy = {
            'select': None,
            },
        # select the default policy, which is flask_login's login_required
        default_ap = login_required,
        templates = {
            'select':'person/select.html',
            'select_one':'person/select_one.html',
            'insert':'person/insert.html',
        },
        # example of altering a callback. when insert successfully, call this user func.
        rex_callback = {
            'insert': {'ok': lambda *args, **kwargs : flash('NEW PERSON!')},
        },
        # disabling a route
        routes_disabled = ['update'],
    )
    c2 = SQLContent( PairRecord,
        default_ap = login_required,
        templates = {
            'select':'pair/select.html',
            'select_one':'pair/select_one.html',
            'insert':'pair/insert.html',
            'update':'pair/update.html'
        },
        reroutes = {
            'insert': 'vicms.update',
            'update': 'vicms.delete', # delete upon update, THIS IS JUST FOR DEMO
            },
        reroutes_kwarg = {
            'insert': {'id':None}, # passthrough
            'update': {'id':None}, # passthrough
            },
    )

    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with vicms
    session = sqlorm.connect(app.config['DBURI'], Base)
    #arch = Arch( [c1, c2], session, url_prefix = '/')
    #bp = arch.generate_blueprint()
    #app.register_blueprint(bp)

    arch = Arch( [c1, c2], session, url_prefix = '/')
    #bp = Arch( [c1, c2], session, url_prefix = '/').generate_blueprint()
    #app.register_blueprint(bp)
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

    # for browser test
    @app.route('/cheat/', methods=['GET'])
    def cheat():
        login_user( PlaceHolderAuth() )
        return 'logged in'

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

    # teardown context for the sqlorm session, init app already handled for us
    #@app.teardown_appcontext
    #def shutdown_session(exception=None):
    #    session.remove()

    return app
