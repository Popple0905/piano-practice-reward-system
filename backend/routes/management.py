import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, Parent, Child

management_bp = Blueprint('management', __name__)

ID_PATTERN = re.compile(r'^[A-Za-z0-9]{1,20}$')

def _validate_child_id(raw_id):
    """Validate ID format (alphanumeric, 1-20 characters). Returns (id_str, error_msg)."""
    if not raw_id:
        return None, None  # Not provided, auto-generate
    raw_id = str(raw_id).strip()
    if not ID_PATTERN.match(raw_id):
        return None, 'ID must contain only letters and numbers, length 1-20'
    return raw_id, None

@management_bp.route('/create-child', methods=['POST'])
@jwt_required()
def create_child():
    """Parent creates a child account"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can create child accounts'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or not data.get('name') or not data.get('password'):
        return jsonify({'error': 'Missing required fields: name and password'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    # Handle custom ID
    custom_id, err = _validate_child_id(data.get('id'))
    if err:
        return jsonify({'error': err}), 400
    if custom_id and Child.query.get(custom_id):
        return jsonify({'error': f'ID "{custom_id}" is already taken'}), 400

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
        'message': 'Child account created',
        'child_id': child.id,
        'name': child.name,
        'age': child.age,
        'created_at': child.created_at.isoformat() + 'Z' if child.created_at else None
    }), 201


@management_bp.route('/delete-child/<string:child_id>', methods=['DELETE'])
@jwt_required()
def delete_child(child_id):
    """Parent deletes a child account"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can delete child accounts'}), 403

    parent_id = int(identity.split('_', 1)[1])

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': 'Child not found or permission denied'}), 404

    child_name = child.name
    db.session.delete(child)
    db.session.commit()

    return jsonify({
        'message': f'Child account "{child_name}" deleted',
        'child_id': child_id
    }), 200


@management_bp.route('/update-child-password/<string:child_id>', methods=['POST'])
@jwt_required()
def update_child_password(child_id):
    """Parent updates a child's password"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can update child passwords'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or not data.get('new_password'):
        return jsonify({'error': 'Missing new password'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': 'Child not found or permission denied'}), 404

    child.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()

    return jsonify({
        'message': f'Password for {child.name} updated',
        'child_id': child.id,
        'child_name': child.name
    }), 200


@management_bp.route('/update-child-name/<string:child_id>', methods=['POST'])
@jwt_required()
def update_child_name(child_id):
    """Parent updates a child's name"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can update child names'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or not data.get('new_name'):
        return jsonify({'error': 'Missing new name'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': 'Child not found or permission denied'}), 404

    old_name = child.name
    child.name = data['new_name']
    db.session.commit()

    return jsonify({
        'message': f'Child name updated from "{old_name}" to "{child.name}"',
        'child_id': child.id,
        'child_name': child.name
    }), 200


@management_bp.route('/update-child-age/<string:child_id>', methods=['POST'])
@jwt_required()
def update_child_age(child_id):
    """Parent updates a child's age"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can update child information'}), 403

    parent_id = int(identity.split('_', 1)[1])

    data = request.get_json()

    if not data or data.get('age') is None:
        return jsonify({'error': 'Missing age'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    child = Child.query.get(child_id)
    if not child or child.parent_id != parent_id:
        return jsonify({'error': 'Child not found or permission denied'}), 404

    child.age = data['age']
    db.session.commit()

    return jsonify({
        'message': f'Age for {child.name} updated to {child.age}',
        'child_id': child.id,
        'child_name': child.name,
        'age': child.age
    }), 200
