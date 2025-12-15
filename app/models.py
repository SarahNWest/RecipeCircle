from app import db, login

@login.user_loader
def load_user(id):
    return None  # Will be implemented when User model is added
