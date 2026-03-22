from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db
import os

def create_app(config_name='development'):
    """应用工厂"""
    app = Flask(__name__)
    
    # 加载配置（默认使用development以便SQLite）
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 启用CORS
    CORS(app)
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.practice import practice_bp
    from routes.awards import awards_bp
    from routes.management import management_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(practice_bp, url_prefix='/api/practice')
    app.register_blueprint(awards_bp, url_prefix='/api/awards')
    app.register_blueprint(management_bp, url_prefix='/api/management')
    
    # 前端文件路径 - 相对于 backend 目录的上一级
    FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    # 提供前端文件
    @app.route('/', methods=['GET'])
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')
    
    @app.route('/<path:filename>', methods=['GET'])
    def serve_files(filename):
        file_path = os.path.join(FRONTEND_DIR, filename)
        if os.path.isfile(file_path):
            return send_from_directory(FRONTEND_DIR, filename)
        # 所有其他路由返回 index.html（支持前端路由）
        return send_from_directory(FRONTEND_DIR, 'index.html')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
