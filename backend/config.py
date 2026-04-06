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
    # Railway MySQL service injects MYSQL_PRIVATE_URL (internal) and DATABASE_URL (may be auto-overridden)
    # Prefer MYSQL_PRIVATE_URL to avoid Railway auto-injected DATABASE_URL conflicts
    _db_url = os.getenv('MYSQL_PRIVATE_URL') or os.getenv('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = _db_url.replace('mysql://', 'mysql+pymysql://', 1) if _db_url else ''

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
