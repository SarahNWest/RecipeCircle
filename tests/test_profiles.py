import pytest
from app.models import User
from app import db


class TestProfileViewing:
    """Tests for viewing user profiles."""
    
    def test_profile_view_as_anonymous(self, client, init_database):
        """Test that anonymous users can view public profiles."""
        response = client.get('/user/testuser')
        
        assert response.status_code == 200
        assert b'testuser' in response.data
        assert b'Log in to follow this user' in response.data
        # Should not show Edit Profile button for anonymous users
        assert b'Edit Profile' not in response.data
    
    def test_profile_view_as_authenticated(self, authenticated_client, init_database):
        """Test that authenticated users can view other profiles with follow button."""
        response = authenticated_client.get('/user/otheruser')
        
        assert response.status_code == 200
        assert b'otheruser' in response.data
        # Should show Follow button since not following yet
        assert b'Follow' in response.data
        assert b'Edit Profile' not in response.data
    
    def test_profile_view_own_profile(self, authenticated_client, init_database):
        """Test that users see Edit Profile link on their own profile."""
        response = authenticated_client.get('/user/testuser')
        
        assert response.status_code == 200
        assert b'testuser' in response.data
        assert b'Edit your profile' in response.data
        # Should not show Follow button on own profile
        assert b'Follow' not in response.data
    
    def test_profile_invalid_username(self, client):
        """Test that viewing a non-existent profile returns 404."""
        response = client.get('/user/nonexistentuser')
        
        assert response.status_code == 404
    
    def test_profile_shows_follower_counts(self, client, init_database, app):
        """Test that profile displays correct follower and following counts."""
        # Set up: have testuser follow otheruser
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            user2 = db.session.query(User).filter_by(username='otheruser').first()
            user1.follow(user2)
            db.session.commit()
        
        # Check otheruser's profile shows 1 follower
        response = client.get('/user/otheruser')
        assert response.status_code == 200
        assert b'1 followers' in response.data or b'Followers: 1' in response.data


class TestFollowUnfollowRoutes:
    """Tests for follow/unfollow functionality."""
    
    def test_follow_route_authenticated(self, authenticated_client, init_database, app):
        """Test that authenticated users can follow other users."""
        response = authenticated_client.post('/follow/otheruser', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'You are following otheruser!' in response.data
        
        # Verify in database
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            user2 = db.session.query(User).filter_by(username='otheruser').first()
            assert user1.is_following(user2) is True
    
    def test_unfollow_route_authenticated(self, authenticated_client, init_database, app):
        """Test that authenticated users can unfollow users they're following."""
        # First follow the user
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            user2 = db.session.query(User).filter_by(username='otheruser').first()
            user1.follow(user2)
            db.session.commit()
        
        # Now unfollow
        response = authenticated_client.post('/unfollow/otheruser', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'You are not following otheruser.' in response.data
        
        # Verify in database
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            user2 = db.session.query(User).filter_by(username='otheruser').first()
            assert user1.is_following(user2) is False
    
    def test_follow_route_anonymous_user(self, client, init_database):
        """Test that anonymous users cannot follow and are redirected with flash message."""
        response = client.post('/follow/otheruser', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please log in to follow users' in response.data
        assert b'Sign In' in response.data or b'Login' in response.data
    
    def test_unfollow_route_anonymous_user(self, client, init_database):
        """Test that anonymous users cannot unfollow."""
        response = client.post('/unfollow/otheruser', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_follow_invalid_username(self, authenticated_client):
        """Test following a non-existent user redirects with flash message."""
        response = authenticated_client.post('/follow/nonexistentuser', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User nonexistentuser not found.' in response.data
    
    def test_unfollow_invalid_username(self, authenticated_client):
        """Test unfollowing a non-existent user redirects with flash message."""
        response = authenticated_client.post('/unfollow/nonexistentuser', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User nonexistentuser not found.' in response.data
    
    def test_follow_self_integration(self, authenticated_client, init_database, app):
        """Test that users cannot follow themselves via the route."""
        response = authenticated_client.post('/follow/testuser', follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user is not following themselves
        with app.app_context():
            user = db.session.query(User).filter_by(username='testuser').first()
            assert user.is_following(user) is False
    
    def test_duplicate_follow_via_route(self, authenticated_client, init_database, app):
        """Test that following a user twice doesn't cause errors."""
        # Follow once
        authenticated_client.post('/follow/otheruser', follow_redirects=True)
        
        # Follow again
        response = authenticated_client.post('/follow/otheruser', follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify still only following once
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            assert user1.following_count() == 1


class TestEditProfile:
    """Tests for editing user profiles."""
    
    def test_edit_profile_page_loads(self, authenticated_client):
        """Test that edit profile page loads for authenticated users."""
        response = authenticated_client.get('/edit_profile')
        
        assert response.status_code == 200
        assert b'Edit Profile' in response.data
    
    def test_edit_profile_requires_login(self, client):
        """Test that edit profile redirects anonymous users to login."""
        response = client.get('/edit_profile', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_edit_profile_update_username(self, authenticated_client, init_database, app):
        """Test updating username via edit profile."""
        response = authenticated_client.post('/edit_profile', data={
            'username': 'updateduser',
            'about_me': 'Updated bio'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Your changes have been saved' in response.data
        
        # Verify in database
        with app.app_context():
            user = db.session.query(User).filter_by(username='updateduser').first()
            assert user is not None
            assert user.about_me == 'Updated bio'
    
    def test_edit_profile_duplicate_username(self, authenticated_client, init_database):
        """Test that editing profile with existing username shows error."""
        response = authenticated_client.post('/edit_profile', data={
            'username': 'otheruser',  # Already exists
            'about_me': 'Test bio'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please use a different username' in response.data
