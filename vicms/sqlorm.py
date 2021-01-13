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

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def make_session(engine, base):
    '''create a session and bind the Base query property to it'''
    sess =  scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
    base.query = sess.query_property()
    return sess

def connect(dburi, base):
    '''easy function to connect to a database, returns a session'''
    engine = create_engine(dburi)
    return make_session(engine, base)
