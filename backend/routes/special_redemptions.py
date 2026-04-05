from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, SpecialRedemption, SpecialRedemptionRecord, Child, Parent
from datetime import datetime

special_redemptions_bp = Blueprint('special_redemptions', __name__)


def _parse_expires_at(value):
    """Parse expires_at string (UTC ISO) to naive UTC datetime, or return None."""
    if not value:
        return None
    try:
        # Handle 'Z' suffix — Python < 3.11 doesn't support it in fromisoformat
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        # Strip tzinfo so it stays consistent with other naive-UTC datetimes in DB
        return dt.replace(tzinfo=None)
    except ValueError:
        return None


@special_redemptions_bp.route('/', methods=['POST'])
@jwt_required()
def create_special_redemption():
    """Parent creates a special redemption item for a child."""
    identity = get_jwt_identity()
    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can create special redemptions'}), 403

    parent_id = int(identity.split('_')[1])
    data = request.get_json()

    if not data or not data.get('child_id') or not data.get('content') or not data.get('points_cost'):
        return jsonify({'error': 'Missing required fields: child_id, content, points_cost'}), 400

    if data['points_cost'] <= 0:
        return jsonify({'error': 'points_cost must be positive'}), 400

    child = Child.query.get(data['child_id'])
    if not child or child.parent_id != parent_id:
        return jsonify({'error': 'Child not found or permission denied'}), 404

    quantity = data.get('quantity')
    if quantity is not None:
        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({'error': 'quantity must be positive'}), 400

    item = SpecialRedemption(
        parent_id=parent_id,
        child_id=data['child_id'],
        content=data['content'],
        points_cost=int(data['points_cost']),
        quantity=quantity,
        expires_at=_parse_expires_at(data.get('expires_at'))
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({
        'message': 'Special redemption created',
        'id': item.id,
        'content': item.content,
        'points_cost': item.points_cost,
        'quantity': item.quantity,
        'expires_at': item.expires_at.isoformat() + 'Z' if item.expires_at else None
    }), 201


@special_redemptions_bp.route('/parent', methods=['GET'])
@jwt_required()
def list_parent_redemptions():
    """Parent lists all special redemptions they created (all children)."""
    identity = get_jwt_identity()
    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can view this'}), 403

    parent_id = int(identity.split('_')[1])
    items = SpecialRedemption.query.filter_by(parent_id=parent_id).order_by(SpecialRedemption.created_at.desc()).all()

    now = datetime.utcnow()
    return jsonify({
        'items': [
            {
                'id': item.id,
                'child_id': item.child_id,
                'child_name': item.child.name,
                'content': item.content,
                'points_cost': item.points_cost,
                'quantity': item.quantity,
                'expires_at': item.expires_at.isoformat() + 'Z' if item.expires_at else None,
                'is_expired': (item.expires_at is not None and item.expires_at < now),
                'created_at': item.created_at.isoformat() + 'Z'
            }
            for item in items
        ]
    }), 200


@special_redemptions_bp.route('/child/<string:child_id>', methods=['GET'])
@jwt_required()
def list_child_redemptions(child_id):
    """Get active (non-expired) special redemptions available to a child."""
    identity = get_jwt_identity()

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        if child.parent_id != parent_id:
            return jsonify({'error': 'Permission denied'}), 403
    elif identity.startswith('child_'):
        if identity.split('_', 1)[1] != child_id:
            return jsonify({'error': 'Permission denied'}), 403
    else:
        return jsonify({'error': 'Invalid token'}), 401

    now = datetime.utcnow()
    items = SpecialRedemption.query.filter_by(child_id=child_id).all()
    active = [
        item for item in items
        if (item.expires_at is None or item.expires_at >= now)
        and (item.quantity is None or item.quantity > 0)
    ]

    return jsonify({
        'child_id': child_id,
        'child_name': child.name,
        'items': [
            {
                'id': item.id,
                'content': item.content,
                'points_cost': item.points_cost,
                'quantity': item.quantity,
                'expires_at': item.expires_at.isoformat() + 'Z' if item.expires_at else None
            }
            for item in active
        ]
    }), 200


@special_redemptions_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_special_redemption(item_id):
    """Parent deletes a special redemption item."""
    identity = get_jwt_identity()
    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can delete special redemptions'}), 403

    parent_id = int(identity.split('_')[1])
    item = SpecialRedemption.query.get(item_id)

    if not item or item.parent_id != parent_id:
        return jsonify({'error': 'Item not found or permission denied'}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Special redemption deleted'}), 200


@special_redemptions_bp.route('/<int:item_id>/redeem', methods=['POST'])
@jwt_required()
def redeem_special_item(item_id):
    """Child redeems a special item using reward points."""
    identity = get_jwt_identity()
    if not identity.startswith('child_'):
        return jsonify({'error': 'Only children can redeem items'}), 403

    child_id = identity.split('_', 1)[1]
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    item = SpecialRedemption.query.get(item_id)
    if not item or item.child_id != child_id:
        return jsonify({'error': 'Item not found or permission denied'}), 404

    now = datetime.utcnow()
    if item.expires_at is not None and item.expires_at < now:
        return jsonify({'error': 'This redemption item has expired'}), 400

    if item.quantity is not None and item.quantity <= 0:
        return jsonify({'error': 'This redemption item is out of stock'}), 400

    if child.game_balance < item.points_cost:
        return jsonify({
            'error': 'Insufficient reward points',
            'current_balance': child.game_balance,
            'required': item.points_cost
        }), 400

    record = SpecialRedemptionRecord(
        child_id=child_id,
        redemption_id=item.id,
        content=item.content,
        points_spent=item.points_cost
    )
    child.game_balance -= item.points_cost
    if item.quantity is not None:
        item.quantity -= 1

    db.session.add(record)
    db.session.commit()

    return jsonify({
        'message': 'Redeemed successfully',
        'content': record.content,
        'points_spent': record.points_spent,
        'remaining_balance': child.game_balance,
        'redeemed_at': record.redeemed_at.isoformat() + 'Z'
    }), 200


@special_redemptions_bp.route('/records/<string:child_id>', methods=['GET'])
@jwt_required()
def get_redemption_records(child_id):
    """Get special redemption history for a child."""
    identity = get_jwt_identity()

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        if child.parent_id != parent_id:
            return jsonify({'error': 'Permission denied'}), 403
    elif identity.startswith('child_'):
        if identity.split('_', 1)[1] != child_id:
            return jsonify({'error': 'Permission denied'}), 403
    else:
        return jsonify({'error': 'Invalid token'}), 401

    records = SpecialRedemptionRecord.query.filter_by(child_id=child_id)\
        .order_by(SpecialRedemptionRecord.redeemed_at.desc()).all()

    return jsonify({
        'child_id': child_id,
        'child_name': child.name,
        'records': [
            {
                'id': r.id,
                'content': r.content,
                'points_spent': r.points_spent,
                'redeemed_at': r.redeemed_at.isoformat() + 'Z'
            }
            for r in records
        ]
    }), 200
