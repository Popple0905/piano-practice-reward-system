from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GameAward, GameRequest, Child, Parent
from datetime import datetime

awards_bp = Blueprint('awards', __name__)

@awards_bp.route('/give', methods=['POST'])
@jwt_required()
def give_game_award():
    """家长发放游戏时间"""
    identity = get_jwt_identity()
    
    if not identity.startswith('parent_'):
        return jsonify({'error': '只有家长可以发放游戏时间'}), 403
    
    parent_id = int(identity.split('_')[1])
    
    data = request.get_json()
    
    if not data or not data.get('child_id') or not data.get('game_minutes'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '家长不存在'}), 404
    
    child = Child.query.get(data['child_id'])
    if not child or child.parent_id != parent_id:
        return jsonify({'error': '孩子不存在或权限不足'}), 404
    
    # 增加孩子的游戏时间
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
        'message': '游戏时间已发放',
        'child_id': child.id,
        'game_minutes': data['game_minutes'],
        'new_balance': child.game_balance
    }), 201

@awards_bp.route('/request', methods=['POST'])
@jwt_required()
def request_game_time():
    """孩子申请游戏时间 (15分钟为单位)"""
    identity = get_jwt_identity()
    
    if not identity.startswith('child_'):
        return jsonify({'error': '只有孩子可以申请游戏时间'}), 403
    
    child_id = identity.split('_', 1)[1]
    
    data = request.get_json()
    
    if not data or not data.get('game_minutes'):
        return jsonify({'error': '缺少游戏时间'}), 400
    
    # 验证是否以15分钟为单位
    if data['game_minutes'] % 15 != 0:
        return jsonify({'error': '申请时间必须以15分钟为单位'}), 400
    
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': '孩子不存在'}), 404
    
    if child.game_balance < data['game_minutes']:
        return jsonify({
            'error': '游戏时间不足',
            'current_balance': child.game_balance,
            'requested': data['game_minutes']
        }), 400
    
    # 创建申请记录并扣除时间
    request_record = GameRequest(
        child_id=child_id,
        game_minutes=data['game_minutes'],
        status='approved'  # 自动批准
    )
    
    child.game_balance -= data['game_minutes']
    
    db.session.add(request_record)
    db.session.commit()
    
    return jsonify({
        'message': '游戏时间申请已批准',
        'game_minutes_used': data['game_minutes'],
        'remaining_balance': child.game_balance,
        'request_id': request_record.id,
        'request_time': request_record.request_date.isoformat()
    }), 200

@awards_bp.route('/balance/<string:child_id>', methods=['GET'])
@jwt_required()
def get_game_balance(child_id):
    """获取孩子的游戏时间余额"""
    identity = get_jwt_identity()
    
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': '孩子不存在'}), 404
    
    # 验证权限
    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
        if child not in parent.children:
            return jsonify({'error': '权限不足'}), 403
    elif identity.startswith('child_'):
        current_child_id = identity.split('_', 1)[1]
        if current_child_id != child_id:
            return jsonify({'error': '权限不足'}), 403
    else:
        return jsonify({'error': '无效的token'}), 401
    
    # 获取家长信息用于展示兑换比例
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
    """获取游戏时间发放历史"""
    identity = get_jwt_identity()
    
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': '孩子不存在'}), 404
    
    # 验证权限
    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
        if child not in parent.children:
            return jsonify({'error': '权限不足'}), 403
    elif identity.startswith('child_'):
        current_child_id = identity.split('_', 1)[1]
        if current_child_id != child_id:
            return jsonify({'error': '权限不足'}), 403
    else:
        return jsonify({'error': '无效的token'}), 401
    
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
                'created_at': a.created_at.isoformat()
            }
            for a in awards
        ]
    }), 200

@awards_bp.route('/request-history/<string:child_id>', methods=['GET'])
@jwt_required()
def get_game_request_history(child_id):
    """获取游戏时间申请历史"""
    identity = get_jwt_identity()
    
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': '孩子不存在'}), 404
    
    # 验证权限
    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
        if child not in parent.children:
            return jsonify({'error': '权限不足'}), 403
    elif identity.startswith('child_'):
        current_child_id = identity.split('_', 1)[1]
        if current_child_id != child_id:
            return jsonify({'error': '权限不足'}), 403
    else:
        return jsonify({'error': '无效的token'}), 401
    
    # 获取查询参数
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
                'request_date': r.request_date.isoformat(),
                'status': r.status
            }
            for r in requests
        ]
    }), 200

@awards_bp.route('/ratio', methods=['GET'])
@jwt_required()
def get_practice_to_game_ratio():
    """获取当前的练琴-游戏时间兑换比例"""
    identity = get_jwt_identity()
    
    if not identity.startswith('parent_') and not identity.startswith('child_'):
        return jsonify({'error': '无效的token'}), 401
    
    if identity.startswith('parent_'):
        parent_id = int(identity.split('_')[1])
        parent = Parent.query.get(parent_id)
    else:
        child_id = identity.split('_', 1)[1]
        child = Child.query.get(child_id)
        parent = child.parent
    
    if not parent:
        return jsonify({'error': '家长不存在'}), 404
    
    return jsonify({
        'practice_to_game_ratio': parent.practice_to_game_ratio,
        'description': f'1分鐘練琴兌換{int(parent.practice_to_game_ratio) if parent.practice_to_game_ratio == int(parent.practice_to_game_ratio) else parent.practice_to_game_ratio}分鐘遊戲時間'
    }), 200

@awards_bp.route('/ratio', methods=['POST'])
@jwt_required()
def set_practice_to_game_ratio():
    """家长设置练琴-游戏时间兑换比例"""
    identity = get_jwt_identity()
    
    if not identity.startswith('parent_'):
        return jsonify({'error': '只有家长可以设置兑换比例'}), 403
    
    parent_id = int(identity.split('_')[1])
    
    data = request.get_json()
    
    if not data or not data.get('ratio') or data['ratio'] <= 0:
        return jsonify({'error': '无效的兑换比例'}), 400
    
    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': '家长不存在'}), 404
    
    parent.practice_to_game_ratio = float(data['ratio'])
    db.session.commit()
    
    return jsonify({
        'message': '兑换比例已更新',
        'new_ratio': parent.practice_to_game_ratio,
        'description': f'1分鐘練琴兌換{int(parent.practice_to_game_ratio) if parent.practice_to_game_ratio == int(parent.practice_to_game_ratio) else parent.practice_to_game_ratio}分鐘遊戲時間'
    }), 200

