# RecipeCircle

A recipe sharing platform built with Flask where users can share their favorite recipes and discover new ones from the community.

## Features

### ✅ Implemented

- **User Authentication**: Register, login, logout with secure password hashing
- **User Profiles**: Public profile pages with avatar (Gravatar), about me, and last seen timestamp
- **Profile Editing**: Users can update their username and about me sections
- **Social Following**: Follow/unfollow other users to build a network
- **Follower Counts**: Display follower and following counts on profiles
- **Anonymous Access**: Public profile viewing with prompts to login for social features
- **Error Handling**: Custom 404 and 500 error pages

### 🚧 Coming Soon

- Recipe creation and sharing
- Personalized home feed (followed users' recipes when logged in)
- Recipe discovery feed for anonymous users
- Testing suite with pytest

## Tech Stack

- **Backend**: Flask 3.1.2, SQLAlchemy 2.0.45
- **Database**: SQLite (development)
- **Auth**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.2.2 with CSRF protection
- **Migrations**: Flask-Migrate 4.1.0

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   flask db upgrade
   ```
5. Run the application:
   ```bash
   flask run
   ```

## Project Status

**Current Milestone**: Milestone 3 Complete (Social Graph - Followers)  
**Next Up**: Adding pytest test suite for existing functionality

### Development Progress

- ✅ Milestone 0: Repository & environment setup
- ✅ Milestone 1: User model & authentication
- ✅ Milestone 2: Profiles & error pages
- ✅ Milestone 3: Follower relationships & social features
- ⏳ Milestone 4: Testing suite
- 📋 Milestone 5: Recipe model & feeds

---

*A portfolio project demonstrating Flask web application development with authentication, database relationships, and social features.*