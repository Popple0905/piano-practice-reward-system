import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, Parent, Child

management_bp = Blueprint('management', __name__)

ID_PATTERN = re.compile(r'^[A-Za-z0-9]{1,20}$')

def _validate_child_id(raw_id):
    """驗證 ID 格式（英文字母與數字，1~20 字元）。回傳 (id_str, error_msg)"""
    if not raw_id:
        return None, None  # 未提供，自動生成
    raw_id = str(raw_id).strip()
    if not ID_PATTERN.match(raw_id):
        return None, 'ID 只能包含英文字母與數字，長度 1~20'
    return raw_id, None

@management_bp.route('/create-child', methods=['POST'])
@jwt_required()
def create_child():
    """家長創建孩子帳號"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': '只有家長可以創建孩子帳號'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or not data.get('name') or not data.get('password'):
        return jsonify({'error': '缺少必要欄位：name 和 password'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '家長不存在'}), 404

    # 處理自訂 ID
    custom_id, err = _validate_child_id(data.get('id'))
    if err:
        return jsonify({'error': err}), 400
    if custom_id and Child.query.get(custom_id):
        return jsonify({'error': f'ID 「{custom_id}」已被使用'}), 400

    child_kwargs = dict(
        parent_id=parent_id,
        name=data['name'],
        age=data.get('age'),
        password_hash=generate_password_hash(data['password'])
    )
    if custom_id:
        child_kwargs['id'] = custom_id

    child = Child(**child_kwargs)
    db.session.add(child)
    db.session.commit()

    return jsonify({
        'message': '孩子帳號已創建',
        'child_id': child.id,
        'name': child.name,
        'age': child.age,
        'created_at': child.created_at.isoformat() if child.created_at else None
    }), 201


@management_bp.route('/delete-child/<string:child_id>', methods=['DELETE'])
@jwt_required()
def delete_child(child_id):
    """家長刪除孩子帳號"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': '只有家長可以刪除孩子帳號'}), 403

    parent_id = int(identity.split('_', 1)[1])

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '家長不存在'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': '孩子不存在或權限不足'}), 404

    child_name = child.name
    db.session.delete(child)
    db.session.commit()

    return jsonify({
        'message': f'孩子帳號 {child_name} 已刪除',
        'child_id': child_id
    }), 200


@management_bp.route('/update-child-password/<string:child_id>', methods=['POST'])
@jwt_required()
def update_child_password(child_id):
    """家長修改孩子密碼"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': '只有家長可以修改孩子密碼'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or not data.get('new_password'):
        return jsonify({'error': '缺少新密碼'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '家長不存在'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': '孩子不存在或權限不足'}), 404

    child.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()

    return jsonify({
        'message': f'孩子 {child.name} 的密碼已更新',
        'child_id': child.id,
        'child_name': child.name
    }), 200


@management_bp.route('/update-child-name/<string:child_id>', methods=['POST'])
@jwt_required()
def update_child_name(child_id):
    """家長修改孩子名稱"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': '只有家長可以修改孩子名稱'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or not data.get('new_name'):
        return jsonify({'error': '缺少新名稱'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '家長不存在'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': '孩子不存在或權限不足'}), 404

    old_name = child.name
    child.name = data['new_name']
    db.session.commit()

    return jsonify({
        'message': f'孩子名稱已從 {old_name} 更新為 {child.name}',
        'child_id': child.id,
        'child_name': child.name
    }), 200


@management_bp.route('/update-child-age/<string:child_id>', methods=['POST'])
@jwt_required()
def update_child_age(child_id):
    """家長修改孩子年齡"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': '只有家長可以修改孩子資料'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or data.get('age') is None:
        return jsonify({'error': '缺少年齡'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '家長不存在'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': '孩子不存在或權限不足'}), 404

    child.age = data['age']
    db.session.commit()

    return jsonify({
        'message': f'孩子 {child.name} 的年齡已更新為 {child.age}',
        'child_id': child.id,
        'child_name': child.name,
        'age': child.age
    }), 200
