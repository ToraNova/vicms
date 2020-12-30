'''
an absolute basic cms architecture
to run:
(in virtualenv @ examples/)
export FLASK_APP=basic
flask run
'''
from flask import Flask, render_template, redirect, url_for
from vicms.basic import Arch
from vicms import sqlorm
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class PersonRecord(sqlorm.ViCMSBase):
    '''an example content class that can be used by the cms library'''
    __tablename__ = "personrec"
    id = Column(Integer, primary_key = True)
    name = Column(String(50),unique=True,nullable=False)
    birthdate =  Column(DateTime(),unique=False, nullable=True)

    # this is called on insertion, decide what to insert and how based on form
    # this is in a try-catch block, raise an exception to abort if necessary
    def __init__(self, reqform):
        self.name = reqform.get("name")
        self.birthdate = None # null

    # this is called on update, decide what to change and how based on form
    # this is in a try-catch block, raise an exception to abort if necessary
    def update(self, reqform):
        self.name = reqform.get("name")

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
    except Exception as e:
        # ignore if table already exist
        #print(e)
        pass

    # define a place to find the templates
    # set url_prefix = '/' to have no url_prefix, leaving it empty will prefix with viauth
    arch = Arch(
        app.config['DBURI'], PersonRecord,
        templates = {
            'select':'select.html',
            'select_one':'select_one.html',
            'insert':'insert.html',
            'update':'update.html'
        },
        reroutes = {
            'insert':'select',
            'update':'select',
            'delete':'select'
        },
        url_prefix = '/'
    )

    arch.init_app(app)

    @app.route('/')
    def root():
        return render_template('home.html')

    return app
