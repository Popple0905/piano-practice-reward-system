from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, PracticeRecord, Child, Parent
from datetime import datetime, date

practice_bp = Blueprint('practice', __name__)

@practice_bp.route('/record', methods=['POST'])
@jwt_required()
def add_practice_record():
    """Child submits a practice record (in 15-min units)"""
    identity = get_jwt_identity()

    if not identity.startswith('child_'):
        return jsonify({'error': 'Only children can add practice records'}), 403

    child_id = identity.split('_', 1)[1]

    data = request.get_json()

    if not data or not data.get('practice_minutes'):
        return jsonify({'error': 'Missing practice duration'}), 400

    # Validate that duration is a multiple of 15
    if data['practice_minutes'] % 15 != 0:
        return jsonify({'error': 'Practice duration must be in 15-minute increments'}), 400

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    # Parse date and time
    record_date = datetime.fromisoformat(data.get('date', datetime.utcnow().isoformat())).date()
    record_time = None
    if data.get('time'):
        try:
            time_obj = datetime.fromisoformat(data.get('time')).time()
            # Round to nearest 5 minutes
            minutes = time_obj.minute
            rounded_minutes = round(minutes / 5) * 5
            hours = time_obj.hour

            # Handle hour overflow from rounding
            if rounded_minutes >= 60:
                hours = (hours + 1) % 24
                rounded_minutes = 0

            record_time = time_obj.replace(hour=hours, minute=rounded_minutes, second=0, microsecond=0)
        except:
            pass

    # Check if a record already exists for this date
    existing = PracticeRecord.query.filter_by(
        child_id=child_id,
        date=record_date
    ).first()

    if existing:
        existing.practice_minutes = data['practice_minutes']
        existing.time = record_time
        existing.notes = data.get('notes')
        existing.status = 'pending'  # Re-submission requires parent approval
    else:
        record = PracticeRecord(
            child_id=child_id,
            date=record_date,
            time=record_time,
            practice_minutes=data['practice_minutes'],
            notes=data.get('notes'),
            status='pending'
        )
        db.session.add(record)

    db.session.commit()

    return jsonify({
        'message': 'Practice record submitted, awaiting parent approval',
        'date': str(record_date),
        'time': str(record_time) if record_time else None,
        'practice_minutes': data['practice_minutes'],
        'status': 'pending'
    }), 201

@practice_bp.route('/record/<int:record_id>/approve', methods=['POST'])
@jwt_required()
def approve_practice_record(record_id):
    """Parent approves a child's practice record"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can approve practice records'}), 403

    parent_id = int(identity.split('_')[1])

    record = PracticeRecord.query.get(record_id)
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    # Verify parent has permission for this child
    parent = Parent.query.get(parent_id)
    if record.child not in parent.children:
        return jsonify({'error': 'Permission denied'}), 403

    if record.status != 'pending':
        return jsonify({'error': f'Record status is {record.status}, cannot approve'}), 400

    # Approve the record
    record.status = 'approved'
    record.approved_at = datetime.utcnow()

    # Calculate reward points earned
    game_minutes = int(record.practice_minutes * parent.practice_to_game_ratio)

    # Add reward points to child's balance
    record.child.game_balance += game_minutes

    db.session.commit()

    return jsonify({
        'message': 'Practice record approved',
        'record_id': record_id,
        'practice_minutes': record.practice_minutes,
        'game_minutes_earned': game_minutes,
        'child_new_balance': record.child.game_balance
    }), 200

@practice_bp.route('/record/<int:record_id>/reject', methods=['POST'])
@jwt_required()
def reject_practice_record(record_id):
    """Parent rejects a child's practice record"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can reject practice records'}), 403

    parent_id = int(identity.split('_')[1])

    record = PracticeRecord.query.get(record_id)
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    # Verify parent has permission for this child
    parent = Parent.query.get(parent_id)
    if record.child not in parent.children:
        return jsonify({'error': 'Permission denied'}), 403

    if record.status != 'pending':
        return jsonify({'error': f'Record status is {record.status}, cannot reject'}), 400

    # Reject the record
    record.status = 'rejected'

    db.session.commit()

    return jsonify({
        'message': 'Practice record rejected',
        'record_id': record_id
    }), 200

@practice_bp.route('/records/<string:child_id>', methods=['GET'])
@jwt_required()
def get_practice_records(child_id):
    """Get a child's practice records"""
    identity = get_jwt_identity()

    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    # Verify permission: parent or the child themselves
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
    status = request.args.get('status')  # pending, approved, rejected

    query = PracticeRecord.query.filter_by(child_id=child_id)

    if start_date:
        query = query.filter(PracticeRecord.date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(PracticeRecord.date <= datetime.fromisoformat(end_date).date())
    if status:
        query = query.filter(PracticeRecord.status == status)

    records = query.order_by(PracticeRecord.date.desc()).all()

    total_approved = sum(r.practice_minutes for r in records if r.status == 'approved')

    return jsonify({
        'child_id': child_id,
        'child_name': child.name,
        'total_records': len(records),
        'approved_records': len([r for r in records if r.status == 'approved']),
        'pending_records': len([r for r in records if r.status == 'pending']),
        'total_approved_minutes': total_approved,
        'records': [
            {
                'id': r.id,
                'date': str(r.date),
                'time': str(r.time) if r.time else None,
                'practice_minutes': r.practice_minutes,
                'status': r.status,
                'notes': r.notes,
                'created_at': r.created_at.isoformat() + 'Z' if r.created_at else None,
                'approved_at': r.approved_at.isoformat() + 'Z' if r.approved_at else None
            }
            for r in records
        ]
    }), 200

@practice_bp.route('/statistics/<string:child_id>', methods=['GET'])
@jwt_required()
def get_statistics(child_id):
    """Get practice statistics for a child"""
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

    # Only count approved records
    records = PracticeRecord.query.filter_by(child_id=child_id, status='approved').all()

    if not records:
        return jsonify({
            'child_id': child_id,
            'total_approved_minutes': 0,
            'average_daily': 0,
            'days_practiced': 0
        }), 200

    total_minutes = sum(r.practice_minutes for r in records)
    days_practiced = len(set(r.date for r in records))

    return jsonify({
        'child_id': child_id,
        'total_approved_minutes': total_minutes,
        'average_daily': total_minutes / days_practiced if days_practiced > 0 else 0,
        'days_practiced': days_practiced
    }), 200

@practice_bp.route('/parent/children', methods=['GET'])
@jwt_required()
def get_parent_children():
    """Parent gets list of all their children with statistics"""
    identity = get_jwt_identity()

    if not identity.startswith('parent_'):
        return jsonify({'error': 'Only parents can access this endpoint'}), 403

    parent_id = int(identity.split('_')[1])
    parent = Parent.query.get(parent_id)

    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    from datetime import timedelta
    children_data = []
    for child in parent.children:
        # Get pending record count
        pending_count = len([r for r in child.practice_records if r.status == 'pending'])

        # Get total approved minutes for the past 30 days
        today = date.today()
        past_30_days_start = today - timedelta(days=30)

        month_records = [r for r in child.practice_records
                        if r.status == 'approved' and r.date >= past_30_days_start]
        total_practice_minutes = sum(r.practice_minutes for r in month_records)

        children_data.append({
            'id': child.id,
            'name': child.name,
            'age': child.age,
            'game_balance': child.game_balance,
            'pending_records': pending_count,
            'total_practice_minutes_past_30_days': total_practice_minutes,
            'practice_records_count': len(child.practice_records),
            'game_requests_count': len(child.game_requests)
        })

    return jsonify({
        'parent_id': parent_id,
        'parent_username': parent.username,
        'practice_to_game_ratio': parent.practice_to_game_ratio,
        'children_count': len(parent.children),
        'children': children_data
    }), 200
