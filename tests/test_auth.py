import pytest
from app.models import User
from app import db


class TestAuthRoutes:
    """Tests for authentication routes."""
    
    def test_register_page_loads(self, client):
        """Test that the register page loads successfully."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page_loads(self, client):
        """Test that the login page loads successfully."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Sign In' in response.data
    
    def test_successful_registration(self, client, app):
        """Test that a new user can register successfully."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check that user was created in database
        with app.app_context():
            user = db.session.query(User).filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.check_password('newpassword123') is True
    
    def test_registration_duplicate_username(self, client, init_database):
        """Test that registration fails with duplicate username."""
        response = client.post('/register', data={
            'username': 'testuser',  # Already exists from init_database
            'email': 'unique@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please use a different username' in response.data
    
    def test_registration_duplicate_email(self, client, init_database):
        """Test that registration fails with duplicate email."""
        response = client.post('/register', data={
            'username': 'uniqueuser',
            'email': 'test@example.com',  # Already exists from init_database
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please use a different email address' in response.data
    
    def test_registration_password_mismatch(self, client):
        """Test that registration fails when passwords don't match."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'differentpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Field must be equal to password' in response.data
    
    def test_successful_login(self, client, init_database):
        """Test that a user can log in successfully."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # After login, should redirect to index
        assert b'testuser' in response.data or b'Profile' in response.data
    
    def test_login_invalid_username(self, client, init_database):
        """Test that login fails with invalid username."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_invalid_password(self, client, init_database):
        """Test that login fails with wrong password."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_logout(self, authenticated_client):
        """Test that a logged-in user can log out."""
        response = authenticated_client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200
        # After logout, should see login link instead of profile
        assert b'Sign In' in response.data or b'Login' in response.data
    
    def test_login_required_redirect(self, client):
        """Test that accessing protected pages redirects to login."""
        response = client.get('/edit_profile', follow_redirects=False)
        
        # Should redirect to login page
        assert response.status_code == 302
        assert '/login' in response.location
