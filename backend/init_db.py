#!/usr/bin/env python
"""Database initialization script - creates test users"""

from app import create_app, db
from models import Parent, Child
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize test data"""
    app = create_app('development')

    with app.app_context():
        # Drop all tables
        db.drop_all()

        # Create all tables
        db.create_all()
        print("✅ Database tables created")

        # Create test parent
        parent = Parent(
            username='testparent',
            email='parent@example.com',
            password_hash=generate_password_hash('parent123')
        )
        db.session.add(parent)
        db.session.commit()
        print(f"✅ Parent created - ID: {parent.id}, username: {parent.username}")

        # Create test child
        child = Child(
            parent_id=parent.id,
            name='Test Child',
            age=10,
            password_hash=generate_password_hash('child123')
        )
        db.session.add(child)
        db.session.commit()
        print(f"✅ Child created - ID: {child.id}, name: {child.name}")

        print("\n========== Test Account Info ==========")
        print(f"Parent login: username='testparent', password='parent123'")
        print(f"Child login: child_id={child.id}, password='child123'")
        print("=======================================")

if __name__ == '__main__':
    init_db()
