import pytest
from app import app as flask_app, db
from app.models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In-memory database
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


@pytest.fixture
def app():
    """Create and configure a test instance of the Flask app."""
    flask_app.config.from_object(TestConfig)
    
    # Create the database and tables
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def init_database(app):
    """Create test users in the database."""
    with app.app_context():
        # Create test users
        user1 = User(username='testuser', email='test@example.com')
        user1.set_password('password123')
        
        user2 = User(username='otheruser', email='other@example.com')
        user2.set_password('password456')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        yield db
        
        # Cleanup is handled by the app fixture


@pytest.fixture
def authenticated_client(client, init_database):
    """A test client that's logged in as testuser."""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    return client
