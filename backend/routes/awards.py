from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GameAward, GameRequest, Child, Parent
from datetime import datetime

awards_bp = Blueprint('awards', __name__)

@awards_bp.route('/give', methods=['POST'])
@jwt_required()
def give_game_award():
    """Parent grants reward points to a child"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can grant reward points'}), 403

    parent_id = int(identity.split('_')[1])

    data = request.get_json()

    if not data or not data.get('child_id') or not data.get('game_minutes'):
        return jsonify({'error': 'Missing required fields'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    child = Child.query.get(data['child_id'])
    if not child or child.parent_id != parent_id:
        return jsonify({'error': 'Child not found or permission denied'}), 404

    # Add reward points to child's balance
    award = GameAward(
        parent_id=parent_id,
        child_id=data['child_id'],
        game_minutes=data['game_minutes'],
        reason=data.get('reason', '')
    )

    child.game_balance += data['game_minutes']

    db.session.add(award)
    db.session.commit()

    return jsonify({
        'message': 'Reward points granted',
        'child_id': child.id,
        'game_minutes': data['game_minutes'],
        'new_balance': child.game_balance
    }), 201

@awards_bp.route('/request', methods=['POST'])
@jwt_required()
def request_game_time():
    """Child redeems reward points (in 15-min units)"""
    identity = get_jwt_identity()

    if not identity.startswith('child_'):
        return jsonify({'error': 'Only children can redeem reward points'}), 403

    child_id = identity.split('_', 1)[1]

    data = request.get_json()

    if not data or not data.get('game_minutes'):
        return jsonify({'error': 'Missing game time amount'}), 400

    # Validate that amount is a multiple of 15
    if data['game_minutes'] % 15 != 0:
        return jsonify({'error': 'Redemption amount must be in 15-minute increments'}), 400

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    if child.game_balance < data['game_minutes']:
        return jsonify({
            'error': 'Insufficient reward points',
            'current_balance': child.game_balance,
            'requested': data['game_minutes']
        }), 400

    # Create redemption record and deduct points
    request_record = GameRequest(
        child_id=child_id,
        game_minutes=data['game_minutes'],
        status='approved'  # Auto-approved
    )

    child.game_balance -= data['game_minutes']

    db.session.add(request_record)
    db.session.commit()

    return jsonify({
        'message': 'Reward points redeemed successfully',
        'game_minutes_used': data['game_minutes'],
        'remaining_balance': child.game_balance,
        'request_id': request_record.id,
        'request_time': request_record.request_date.isoformat() + 'Z'
    }), 200

@awards_bp.route('/balance/<string:child_id>', methods=['GET'])
@jwt_required()
def get_game_balance(child_id):
    """Get a child's reward points balance"""
    identity = get_jwt_identity()

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    # Verify permission
    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
        if child not in parent.children:
            return jsonify({'error': 'Permission denied'}), 403
    elif identity.startswith('child_'):
        current_child_id = identity.split('_', 1)[1]
        if current_child_id != child_id:
            return jsonify({'error': 'Permission denied'}), 403
    else:
        return jsonify({'error': 'Invalid token'}), 401

    # Get parent info for displaying the conversion ratio
    parent = child.parent

    return jsonify({
        'child_id': child.id,
        'child_name': child.name,
        'game_balance': child.game_balance,
        'practice_to_game_ratio': parent.practice_to_game_ratio
    }), 200

@awards_bp.route('/history/<string:child_id>', methods=['GET'])
@jwt_required()
def get_award_history(child_id):
    """Get reward points award history for a child"""
    identity = get_jwt_identity()

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    # Verify permission
    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
        if child not in parent.children:
            return jsonify({'error': 'Permission denied'}), 403
    elif identity.startswith('child_'):
        current_child_id = identity.split('_', 1)[1]
        if current_child_id != child_id:
            return jsonify({'error': 'Permission denied'}), 403
    else:
        return jsonify({'error': 'Invalid token'}), 401

    awards = GameAward.query.filter_by(child_id=child_id).order_by(GameAward.created_at.desc()).all()

    return jsonify({
        'child_id': child.id,
        'child_name': child.name,
        'total_awards': len(awards),
        'total_minutes_given': sum(a.game_minutes for a in awards),
        'awards': [
            {
                'id': a.id,
                'game_minutes': a.game_minutes,
                'reason': a.reason,
                'created_at': a.created_at.isoformat() + 'Z'
            }
            for a in awards
        ]
    }), 200

@awards_bp.route('/request-history/<string:child_id>', methods=['GET'])
@jwt_required()
def get_game_request_history(child_id):
    """Get reward points redemption history for a child"""
    identity = get_jwt_identity()

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    # Verify permission
    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
        if child not in parent.children:
            return jsonify({'error': 'Permission denied'}), 403
    elif identity.startswith('child_'):
        current_child_id = identity.split('_', 1)[1]
        if current_child_id != child_id:
            return jsonify({'error': 'Permission denied'}), 403
    else:
        return jsonify({'error': 'Invalid token'}), 401

    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = GameRequest.query.filter_by(child_id=child_id)

    if start_date:
        query = query.filter(GameRequest.request_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(GameRequest.request_date <= datetime.fromisoformat(end_date))

    requests = query.order_by(GameRequest.request_date.desc()).all()

    return jsonify({
        'child_id': child.id,
        'child_name': child.name,
        'total_requests': len(requests),
        'total_minutes_used': sum(r.game_minutes for r in requests),
        'requests': [
            {
                'id': r.id,
                'game_minutes': r.game_minutes,
                'request_date': r.request_date.isoformat() + 'Z',
                'status': r.status
            }
            for r in requests
        ]
    }), 200

@awards_bp.route('/ratio', methods=['GET'])
@jwt_required()
def get_practice_to_game_ratio():
    """Get the current practice-to-reward conversion ratio"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_') and not identity.startswith('child_'):
        return jsonify({'error': 'Invalid token'}), 401

    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
    else:
        child_id = identity.split('_', 1)[1]
        child = Child.query.get(child_id)
        parent = child.parent

    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    ratio = parent.practice_to_game_ratio
    ratio_display = int(ratio) if ratio == int(ratio) else ratio

    return jsonify({
        'practice_to_game_ratio': ratio,
        'description': f'1 min practice = {ratio_display} reward point(s)'
    }), 200

@awards_bp.route('/ratio', methods=['POST'])
@jwt_required()
def set_practice_to_game_ratio():
    """Parent sets the practice-to-reward conversion ratio"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can set the conversion ratio'}), 403

    parent_id = int(identity.split('_')[1])

    data = request.get_json()

    if not data or not data.get('ratio') or data['ratio'] <= 0:
        return jsonify({'error': 'Invalid conversion ratio'}), 400

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    parent.practice_to_game_ratio = float(data['ratio'])
    db.session.commit()

    ratio = parent.practice_to_game_ratio
    ratio_display = int(ratio) if ratio == int(ratio) else ratio

    return jsonify({
        'message': 'Conversion ratio updated',
        'new_ratio': ratio,
        'description': f'1 min practice = {ratio_display} reward point(s)'
    }), 200
