from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, Parent, Child
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/parent/register', methods=['POST'])
def parent_register():
    """家长注册"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    if Parent.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    parent = Parent(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(parent)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'parent_id': parent.id
    }), 201

@auth_bp.route('/parent/login', methods=['POST'])
def parent_login():
    """家长登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '缺少用户名或密码'}), 400
    
    parent = Parent.query.filter_by(username=data['username']).first()
    
    if not parent or not check_password_hash(parent.password_hash, data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    access_token = create_access_token(identity=f"parent_{parent.id}")
    
    return jsonify({
        'access_token': access_token,
        'parent_id': parent.id,
        'username': parent.username
    }), 200

@auth_bp.route('/child/register', methods=['POST'])
def child_register():
    """孩子注册"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('password') or not data.get('parent_id'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    parent = Parent.query.get(data['parent_id'])
    if not parent:
        return jsonify({'error': '家长不存在'}), 404
    
    child = Child(
        parent_id=data['parent_id'],
        name=data['name'],
        age=data.get('age'),
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(child)
    db.session.commit()
    
    return jsonify({
        'message': '孩子账户创建成功',
        'child_id': child.id
    }), 201

@auth_bp.route('/child/login', methods=['POST'])
def child_login():
    """孩子登录"""
    data = request.get_json()
    
    if not data or not data.get('child_id') or not data.get('password'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    child = Child.query.get(data['child_id'])
    
    if not child or not check_password_hash(child.password_hash, data['password']):
        return jsonify({'error': '孩子ID或密码错误'}), 401
    
    access_token = create_access_token(identity=f"child_{child.id}")
    
    return jsonify({
        'access_token': access_token,
        'child_id': child.id,
        'name': child.name
    }), 200

@auth_bp.route('/parent/change-password', methods=['POST'])
@jwt_required()
def parent_change_password():
    """家長修改自己的密碼"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': '權限不足'}), 403

    parent_id = int(identity.split('_', 1)[1])
    data = request.get_json()

    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': '缺少目前密碼或新密碼'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '用戶不存在'}), 404

    if not check_password_hash(parent.password_hash, data['current_password']):
        return jsonify({'error': '目前密碼錯誤'}), 401

    if len(data['new_password']) < 4:
        return jsonify({'error': '新密碼至少需要 4 個字元'}), 400

    parent.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()

    return jsonify({'message': '密碼已更新'}), 200


@auth_bp.route('/parent/me', methods=['GET'])
@jwt_required()
def get_parent_info():
    """获取当前家长信息"""
    identity = get_jwt_identity()
    
    if identity['user_type'] != 'parent':
        return jsonify({'error': '权限不足'}), 403
    
    parent = Parent.query.get(identity['user_id'])
    
    if not parent:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'parent_id': parent.id,
        'username': parent.username,
        'email': parent.email,
        'children': [
            {
                'child_id': c.id,
                'name': c.name,
                'age': c.age,
                'game_balance': c.game_balance
            }
            for c in parent.children
        ]
    }), 200
