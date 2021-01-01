from examples import basic

def test_config():
    """Test create_app without passing test config."""
    assert not basic.create_app().testing
    assert basic.create_app({"TESTING": True}).testing
