'''
an absolute basic cms architecture
to run:
(in virtualenv @ examples/)
export FLASK_APP=basic
flask run
'''
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from vicms.basic import Arch, SQLContent
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

    # define a place to find the templates and the content sqlorm class
    c1 = SQLContent( PersonRecord,
        templates = {
            'select':'person/select.html',
            'select_one':'person/select_one.html',
            'insert':'person/insert.html',
            'update':'person/update.html'
        },
        # example of altering a callback. when insert successfully, call this user func.
        rex_callback = {
            'insert': {'ok': lambda *args, **kwargs : flash('NEW PERSON!')},
        },
    )
    c2 = SQLContent( PairRecord,
        templates = {
            'select':'pair/select.html',
            'select_one':'pair/select_one.html',
            'insert':'pair/insert.html',
            'update':'pair/update.html'
        },
        reroutes = {
            'insert': 'utest',
            'delete': 'upass',
        },
        reroutes_kwarg = {
            'insert': {'var':'oaktree'}, # when we are rerouted after 'insert'
            'delete': {'id': None}, # use None to allow passthrough, typically the ID of the inserted/updated/delete object
        },
    )

    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with vicms
    session = sqlorm.connect(app.config['DBURI'], Base)
    arch = Arch( [c1, c2], session, url_prefix = '/')
    #bp = Arch( [c1, c2], session, url_prefix = '/').generate_blueprint()
    #app.register_blueprint(bp)
    arch.init_app(app)

    @app.route('/')
    def root():
        return render_template('home.html')

    @app.route('/kwarg/<var>/')
    def utest(var):
        pr = PairRecord.query.all()
        return render_template('pair/select.html', data=pr) + var

    @app.route('/pass/<id>/')
    def upass(id):
        return '%s delete ok' % id

    # teardown context for the sqlorm session, init_app already handled it for us
    #@app.teardown_appcontext
    #def shutdown_session(exception=None):
    #    session.remove()

    return app
