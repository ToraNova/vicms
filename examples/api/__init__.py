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
from vicms.api import SQLContent
from vicms.api.withauth import Arch, SQLContent as AuthSQLContent
from vicms import SQLContentMixin, sqlorm
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
    c1 = SQLContent( PersonRecord, routes_disabled=[] )
    c2 = AuthSQLContent( PairRecord,
            access_policy = {
                'select': None,
            },
            default_ap = login_required, routes_disabled=[]
        )

    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with vicms
    session = sqlorm.connect(app.config['DBURI'], Base)
    arch = Arch( [c1, c2], session, url_prefix = '/apitest')
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
