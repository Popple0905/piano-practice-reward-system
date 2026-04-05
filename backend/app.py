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

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
