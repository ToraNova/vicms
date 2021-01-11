#--------------------------------------------------
# fsqlite.py (sqlalchemy ORM base)
# this file is static and should not be tampered with
# it initializes the required base models for the db engine
# introduced 8/12/2018
# migrated from rapidflask to miniflask (22 Jul 2020)
# migrated from miniflask to vials project (29 Nov 2020)
# ToraNova 2020
# chia_jason96@live.com
#--------------------------------------------------

import datetime
from collections import namedtuple
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime

DBstruct = namedtuple("DBstruct", ["engine","metadata","session","base"])
#Base = declarative_base() # removed since v0.1.2, force user to use their own declarative base

def make_dbstruct(dburi, base):
    '''deprecated, but kept for references'''
    engine = create_engine(dburi)
    metadata = MetaData(bind=engine)
    session = make_session(engine, base)
    base = declarative_base()
    base.query = session.query_property()
    return DBstruct(engine, metadata, session, base)

def make_session(engine, base):
    '''create a session and bind the Base query property to it'''
    sess =  scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
    base.query = sess.query_property()
    return sess

def connect(dburi, base):
    '''easy function to connect to a database, returns a session'''
    engine = create_engine(dburi)
    return make_session(engine, base)

class ViCMSBase:

    def formgen_assist(session):
        return None

    def select_assist(self):
        return None

    # create table if not exist on dburi
    @classmethod
    def create_table(cls, dburi):
        engine = create_engine(dburi)
        cls.__table__.create(engine, checkfirst=True)
        engine.dispose() #house keeping

    # check if table exists in dburi
    @classmethod
    def table_exists(cls, dburi):
        engine = create_engine(dburi)
        ins = inspect(engine)
        res = cls.__tablename__ in ins.get_table_names()
        engine.dispose()
        return res
