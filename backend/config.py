import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    # Use SQLite for local development and testing
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///piano_app.db?timeout=30'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'timeout': 30}}

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
