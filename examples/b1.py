import os
import tempfile
import pytest

from examples import basic

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_file = tempfile.mkstemp()
    db_uri = 'sqlite:///%s' % db_file
    app = basic.create_app({"TESTING": True, "DBURI": db_uri})

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
    assert b'href="/personrec/"' in rv.data
    assert b'href="/pairrec/"' in rv.data

    rv = client.get('/personrec/insert')
    assert rv.status_code == 200
    rv = client.get('/pairrec/insert')
    assert rv.status_code == 200

    rv = client.post('/personrec/insert', data=dict(name="jason", birthdate="1996-06-26"), follow_redirects=True)
    rv = client.post('/personrec/insert', data=dict(name="ting", birthdate="1996-10-02"), follow_redirects=True)
    assert rv.status_code == 200
    assert b'NEW PERSON!' in rv.data
    assert b'jason, 1996-06-26' in rv.data
    assert b'ting, 1996-10-02' in rv.data

    rv = client.get('/personrec/1')
    assert b'<h1>jason</h1>' in rv.data

    rv = client.get('/pairrec/insert')
    assert b'jason' in rv.data and b'ting' in rv.data

    rv = client.post('/pairrec/insert', data=dict(aid="1",bid="2"), follow_redirects=True)
    assert b'jason ting' in rv.data
    assert b'oaktree' in rv.data

    rv = client.get('/pairrec/update/1')
    assert b'jason' in rv.data and b'ting' in rv.data

    rv = client.post('/pairrec/update/1', data=dict(aid="1", bid="1"), follow_redirects=True)
    assert b'a person may not pair with themself' in rv.data

    rv = client.get('/pairrec/')
    assert b'jason ting' in rv.data

    rv = client.post('/personrec/update/2', data=dict(name="ting2", birthdate="1996-10-02"), follow_redirects=True)

    rv = client.get('/pairrec/1')
    assert b'jason' in rv.data and b'ting2' in rv.data

    rv = client.get('/pairrec/delete/1', follow_redirects=True)
    assert b'1 delete ok' in rv.data
