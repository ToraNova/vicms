import os
import tempfile
import pytest

from examples import api

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_file = tempfile.mkstemp()
    db_uri = 'sqlite:///%s' % db_file
    app = api.create_app({"TESTING": True, "DBURI": db_uri})

    # create the database and load test data
    with app.app_context():
        pass
    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_file)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_case(client):

    rv = client.get('/')
    assert b'vicms-api: test app' in rv.data

    rv = client.get('/apitest/personrec/')
    assert b'[]' == rv.data

    rv = client.get('/apitest/personrec/insert')
    assert rv.status_code == 400

    rv = client.post('/apitest/personrec/insert', data=dict(name='jason', birthdate='1996-03-31'))
    assert b'{"id": 1, "name": "jason", "birthdate": "1996-03-31T00:00:00"}' == rv.data
    rv = client.post('/apitest/personrec/insert', data=dict(name='ting', birthdate='1998-02-02'))
    assert b'{"id": 2, "name": "ting", "birthdate": "1998-02-02T00:00:00"}' == rv.data
    rv = client.post('/apitest/personrec/insert', data=dict(name='syun', birthdate='1992-01-16'))

    rv = client.post('/apitest/personrec/insert', data=dict(name='syun', birthdate='1992-01-16'))
    assert b'{"err":"integrity error."}' == rv.data
    rv = client.post('/apitest/personrec/update/1', data=dict(name='syun', birthdate='1992-01-16'))
    assert b'{"err":"integrity error."}' == rv.data

    rv = client.get('/apitest/personrec/')
    assert b'[{"id": 1, "name": "jason", "birthdate": "1996-03-31T00:00:00"}, {"id": 2, "name": "ting", "birthdate": "1998-02-02T00:00:00"}, {"id": 3, "name": "syun", "birthdate": "1992-01-16T00:00:00"}]' == rv.data

    rv = client.get('/apitest/personrec/1')
    assert b'{"id": 1, "name": "jason", "birthdate": "1996-03-31T00:00:00"}' == rv.data

    rv = client.get('/apitest/personrec/delete/3')
    assert b'{"err":"none"}' == rv.data

    rv = client.get('/apitest/personrec/3')
    assert rv.status_code == 404

    rv = client.get('/apitest/pairrec/')
    assert b'[]' == rv.data

    rv = client.post('/apitest/pairrec/insert', data=dict(aid="1",bid="2"))
    assert rv.status_code == 401

    rv = client.post('/apitest/pairrec/update/1', data=dict(aid="1",bid="2"))
    assert rv.status_code == 401

    rv = client.get('/apitest/pairrec/delete/1')
    assert rv.status_code == 401

    rv = client.get('/login/')
    assert b'logged in' == rv.data

    rv = client.post('/apitest/pairrec/insert', data=dict(aid="1",bid="2"))
    assert rv.status_code == 200

    rv = client.get('/apitest/pairrec/')
    assert b'[{"id": 1, "aid": 1, "bid": 2}]' == rv.data
