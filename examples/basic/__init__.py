'''
an absolute basic cms architecture
to run:
(in virtualenv @ examples/)
export FLASK_APP=basic
flask run
'''
from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from vicms.basic import Arch, ViContent
from vicms import sqlorm, ViCMSMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

# users declare their own declarative Base, or use ones that are provided by other libs
# i.e., viauth's sqlorm.Base
Base = sqlorm.declarative_base()

class PersonRecord(ViCMSMixin, Base):
    '''an example content class that can be used by the cms library'''
    __tablename__ = "personrec"
    id = Column(Integer, primary_key = True)
    name = Column(String(50),unique=True,nullable=False)
    birthdate = Column(DateTime(),unique=False, nullable=True)

    def strdate(self):
        return '' if not self.birthdate else self.birthdate.strftime("%Y-%m-%d")

    def formgen_assist(session):
        return None

    # this is called on select/select_one routes to provide auxliary data
    # the provided value can be accessed from the 'auxd' variable
    @classmethod
    def select_assist(cls):
        return None

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

class PairRecord(ViCMSMixin, Base):
    __tablename__ = "pairrec"
    id = Column(Integer, primary_key = True)
    aid = Column(Integer, ForeignKey('personrec.id'), nullable=True)
    bid = Column(Integer, ForeignKey('personrec.id'), nullable=True)
    aperson = relationship("PersonRecord", foreign_keys=[aid])
    bperson = relationship("PersonRecord", foreign_keys=[bid])

    # this is called on insertion GETs, a variable form_data is returned to jinja to help
    # dynamic form creation (if necessary, can be left out)
    def formgen_assist(session):
        p = PersonRecord.query.all()
        return p if p else []

    # this is called on select/select_one routes to provide auxliary data
    # the provided value can be accessed from the 'auxd' variable
    @classmethod
    def select_assist(cls):
        return None

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
    c1 = ViContent( PersonRecord,
        templates = {
            'select':'person/select.html',
            'select_one':'person/select_one.html',
            'insert':'person/insert.html',
            'update':'person/update.html'
        }
    )
    c2 = ViContent( PairRecord,
        templates = {
            'select':'pair/select.html',
            'select_one':'pair/select_one.html',
            'insert':'pair/insert.html',
            'update':'pair/update.html'
        },
        reroutes = {},
        reroutes_kwarg = {},
    )

    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with vicms
    arch = Arch( app.config['DBURI'], Base, [c1, c2], url_prefix = '/')
    arch.init_app(app)

    @app.route('/')
    def root():
        return render_template('home.html')

    return app
