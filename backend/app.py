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
    from routes.lottery import lottery_bp
    from routes.ichiban import ichiban_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(practice_bp, url_prefix='/api/practice')
    app.register_blueprint(awards_bp, url_prefix='/api/awards')
    app.register_blueprint(management_bp, url_prefix='/api/management')
    app.register_blueprint(special_redemptions_bp, url_prefix='/api/special-redemptions')
    app.register_blueprint(lottery_bp, url_prefix='/api/lottery')
    app.register_blueprint(ichiban_bp, url_prefix='/api/ichiban')

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
        ('special_redemptions', 'lottery_draw_result_id',
         'ALTER TABLE special_redemptions ADD COLUMN lottery_draw_result_id INTEGER REFERENCES lottery_draw_results(id)'),
        ('lottery_rounds', 'mode',
         "ALTER TABLE lottery_rounds ADD COLUMN mode VARCHAR(20) DEFAULT 'random'"),
        ('lottery_rounds', 'total_draws',
         'ALTER TABLE lottery_rounds ADD COLUMN total_draws INTEGER DEFAULT 0'),
        ('lottery_prizes', 'grade',
         'ALTER TABLE lottery_prizes ADD COLUMN grade VARCHAR(10)'),
        ('lottery_prizes', 'total_quantity',
         'ALTER TABLE lottery_prizes ADD COLUMN total_quantity INTEGER'),
        ('lottery_prizes', 'remaining_quantity',
         'ALTER TABLE lottery_prizes ADD COLUMN remaining_quantity INTEGER'),
        ('lottery_draw_results', 'grade',
         'ALTER TABLE lottery_draw_results ADD COLUMN grade VARCHAR(10)'),
    ]

    # Backfills that must hold regardless of how the column was created. Adding a column
    # WITH a DEFAULT populates existing rows on both SQLite and MySQL, but `mode` decides
    # whether pre-existing lottery rounds stay visible, so make it explicit and idempotent.
    BACKFILLS = [
        ('lottery_rounds', 'mode',
         "UPDATE lottery_rounds SET mode = 'random' WHERE mode IS NULL"),
    ]

    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    def _has_column(table, column):
        """Fresh inspection — the cached inspector above can be stale after an ALTER."""
        return column in {c['name'] for c in inspect(db.engine).get_columns(table)}

    for table, column, sql in MIGRATIONS:
        if table not in existing_tables:
            continue
        existing_cols = {c['name'] for c in inspector.get_columns(table)}
        if column in existing_cols:
            continue
        try:
            db.session.execute(text(sql))
            db.session.commit()
            app.logger.info(f'[migrate] Added column {table}.{column}')
        except Exception:
            # Gunicorn boots several workers, each calling create_app(), so two of them can
            # race on the same ALTER. Losing that race is fine — but only if the column is
            # genuinely there now. Anything else is a real failure and must surface.
            db.session.rollback()
            if not _has_column(table, column):
                raise
            app.logger.info(f'[migrate] {table}.{column} already added concurrently')

    for table, column, sql in BACKFILLS:
        if table in existing_tables and _has_column(table, column):
            db.session.execute(text(sql))
            db.session.commit()

if __name__ == '__main__':
    env = 'production' if os.getenv('RAILWAY_ENVIRONMENT') else 'development'
    app = create_app(env)
    port = int(os.getenv('PORT', 5000))
    app.run(debug=(env == 'development'), host='0.0.0.0', port=port)
