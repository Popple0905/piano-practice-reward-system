from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db
import os

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration (defaults to development with SQLite)
    app.config.from_object(config[config_name])

    # Initialize database
    db.init_app(app)

    # Initialize JWT
    jwt = JWTManager(app)

    # Enable CORS
    CORS(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.practice import practice_bp
    from routes.awards import awards_bp
    from routes.management import management_bp
    from routes.special_redemptions import special_redemptions_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(practice_bp, url_prefix='/api/practice')
    app.register_blueprint(awards_bp, url_prefix='/api/awards')
    app.register_blueprint(management_bp, url_prefix='/api/management')
    app.register_blueprint(special_redemptions_bp, url_prefix='/api/special-redemptions')

    # Frontend file path - one level up from the backend directory
    FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

    # Serve frontend files
    @app.route('/', methods=['GET'])
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/<path:filename>', methods=['GET'])
    def serve_files(filename):
        file_path = os.path.join(FRONTEND_DIR, filename)
        if os.path.isfile(file_path):
            return send_from_directory(FRONTEND_DIR, filename)
        # All other routes return index.html (supports frontend routing)
        return send_from_directory(FRONTEND_DIR, 'index.html')

    # Create database tables and apply any missing column migrations
    with app.app_context():
        db.create_all()
        _auto_migrate(app)

    return app


def _auto_migrate(app):
    """Add any columns that exist in models but are missing from the live DB.

    Each entry: (table_name, column_name, ALTER TABLE SQL).
    Safe to run repeatedly — skips columns that already exist.
    """
    MIGRATIONS = [
        ('children', 'lottery_tickets',
         'ALTER TABLE children ADD COLUMN lottery_tickets INTEGER DEFAULT 0'),
    ]

    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    for table, column, sql in MIGRATIONS:
        if table not in existing_tables:
            continue
        existing_cols = {c['name'] for c in inspector.get_columns(table)}
        if column not in existing_cols:
            db.session.execute(text(sql))
            db.session.commit()
            app.logger.info(f'[migrate] Added column {table}.{column}')

if __name__ == '__main__':
    env = 'production' if os.getenv('RAILWAY_ENVIRONMENT') else 'development'
    app = create_app(env)
    port = int(os.getenv('PORT', 5000))
    app.run(debug=(env == 'development'), host='0.0.0.0', port=port)
