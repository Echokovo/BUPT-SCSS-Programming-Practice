import sys, os
sys.path.append((os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))))

import pytest
from app import create_app_debug
from models.database import db


@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    app = create_app_debug()
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test"
    })

    yield app


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_setup(app):
    """Initialize and drop database before and after tests."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()