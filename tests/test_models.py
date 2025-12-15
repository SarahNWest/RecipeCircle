import pytest
from app.models import User
from app import db


class TestUserModel:
    """Tests for the User model."""
    
    def test_password_hashing(self, app):
        """Test that password hashing works correctly."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            
            # Password should be hashed, not stored in plain text
            assert user.password_hash != 'testpassword'
            
            # Check password should work with correct password
            assert user.check_password('testpassword') is True
            
            # Check password should fail with wrong password
            assert user.check_password('wrongpassword') is False
    
    def test_avatar(self, app):
        """Test that avatar generation works."""
        with app.app_context():
            user = User(username='john', email='john@example.com')
            
            # Avatar should return a Gravatar URL
            avatar_url = user.avatar(128)
            assert 'gravatar.com' in avatar_url
            assert 'd=identicon' in avatar_url
            assert 's=128' in avatar_url
    
    def test_follow_unfollow(self, app, init_database):
        """Test following and unfollowing users."""
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            user2 = db.session.query(User).filter_by(username='otheruser').first()
            
            # Initially, users should not be following each other
            assert user1.is_following(user2) is False
            assert user2.is_following(user1) is False
            
            # Test follow
            user1.follow(user2)
            db.session.commit()
            assert user1.is_following(user2) is True
            assert user2.is_following(user1) is False
            
            # Test follower counts
            assert user1.following_count() == 1
            assert user1.followers_count() == 0
            assert user2.following_count() == 0
            assert user2.followers_count() == 1
            
            # Test unfollow
            user1.unfollow(user2)
            db.session.commit()
            assert user1.is_following(user2) is False
            assert user1.following_count() == 0
            assert user2.followers_count() == 0
    
    def test_follow_self(self, app, init_database):
        """Test that a user cannot follow themselves."""
        with app.app_context():
            user = db.session.query(User).filter_by(username='testuser').first()
            
            # Following self should not work
            user.follow(user)
            db.session.commit()
            assert user.is_following(user) is False
            assert user.following_count() == 0
    
    def test_duplicate_follow(self, app, init_database):
        """Test that following a user twice doesn't create duplicate relationships."""
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            user2 = db.session.query(User).filter_by(username='otheruser').first()
            
            # Follow once
            user1.follow(user2)
            db.session.commit()
            count_after_first = user1.following_count()
            
            # Follow again (should be idempotent)
            user1.follow(user2)
            db.session.commit()
            count_after_second = user1.following_count()
            
            assert count_after_first == count_after_second == 1
    
    def test_unfollow_not_following(self, app, init_database):
        """Test that unfollowing a user you're not following doesn't cause errors."""
        with app.app_context():
            user1 = db.session.query(User).filter_by(username='testuser').first()
            user2 = db.session.query(User).filter_by(username='otheruser').first()
            
            # Unfollow without following first
            user1.unfollow(user2)
            db.session.commit()
            
            # Should not cause errors and counts should remain 0
            assert user1.following_count() == 0
            assert user2.followers_count() == 0
