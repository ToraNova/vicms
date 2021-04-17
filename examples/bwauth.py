import os
import tempfile
import pytest

from examples import withauth

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_file = tempfile.mkstemp()
    db_uri = 'sqlite:///%s' % db_file
    app = withauth.create_app({"TESTING": True, "DBURI": db_uri})

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

    rv = client.post('/personrec/insert', data=dict(name="jason",birthdate="1996-06-26"), follow_redirects=True)
    assert rv.status_code == 401
    rv = client.get('/pairrec/')
    assert rv.status_code == 401
    rv = client.get('/personrec/')
    assert rv.status_code == 200

    rv = client.post('/login', data=dict(username="tester", password="test123"), follow_redirects=True)
    assert rv.status_code == 200

    rv = client.post('/personrec/insert', data=dict(name="jason",birthdate="1996-07-26"), follow_redirects=False)
    rv = client.post('/personrec/insert', data=dict(name="ting",birthdate="1996-12-02"), follow_redirects=True)
    assert rv.status_code == 200
    assert b'NEW PERSON!' in rv.data
    assert b'jason, 1996-07-26' in rv.data
    assert b'ting, 1996-12-02' in rv.data

    # disabled route test
    rv = client.get('/personrec/update/1')
    assert rv.status_code == 404
    rv = client.post('/personrec/update/1', data=dict(name="john",birthdate="1990-11-02"))
    assert rv.status_code == 404

    rv = client.get('/pairrec/insert')
    assert b'jason' in rv.data and b'ting' in rv.data

    rv = client.post('/pairrec/insert', data=dict(aid="1",bid="2"), follow_redirects=True)
    assert b'jason' in rv.data and b'ting' in rv.data
    assert b'selected' in rv.data and b'update' in rv.data # ensure this is the update page(reroute test with passthrough 'None' kwargs)
    rv = client.get('/pairrec/')
    assert b'jason ting' in rv.data

    rv = client.post('/pairrec/update/1', data=dict(aid="2", bid="1"), follow_redirects=True)
    assert 'successfully deleted' # reroute update to delete, passthrough ID

    rv = client.get('/pairrec/')
    assert rv.status_code == 200
    assert b'jason ting' not in rv.data

    rv = client.get('/logout')
    assert rv.status_code == 200

    rv = client.get('/pairrec/')
    assert rv.status_code == 401

    rv = client.get('/personrec/')
    assert b'jason, 1996-07-26' in rv.data
    assert b'ting, 1996-12-02' in rv.data
