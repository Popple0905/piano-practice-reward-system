import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Child, Parent, LotteryRound, LotteryPrize, LotteryDrawResult, SpecialRedemption
from routes.lottery_common import (
    MODE_RANDOM, parse_identity as _parse_identity, check_child_access, award_prize_to_child,
)

lottery_bp = Blueprint('lottery', __name__)


def _build_slots(prizes):
    """Expand prizes into a 100-element list according to probability."""
    slots = []
    for p in prizes:
        slots.extend([p] * p.probability)
    return slots


def _round_to_dict(rnd, include_prizes=True):
    data = {
        'id': rnd.id,
        'child_id': rnd.child_id,
        'parent_id': rnd.parent_id,
        'mode': rnd.mode,
        'pity_limit': rnd.pity_limit,
        'draws_used': rnd.draws_used,
        'status': rnd.status,
        'jackpot_hit': rnd.jackpot_hit,
        'draws_until_pity': max(0, rnd.pity_limit - rnd.draws_used),
        'created_at': rnd.created_at.isoformat() + 'Z',
        'finished_at': rnd.finished_at.isoformat() + 'Z' if rnd.finished_at else None,
    }
    if include_prizes:
        data['prizes'] = [
            {'id': p.id, 'name': p.name, 'probability': p.probability, 'is_jackpot': p.is_jackpot}
            for p in rnd.prizes
        ]
    return data


# ── POST /rounds ──────────────────────────────────────────────────────────────

@lottery_bp.route('/rounds', methods=['POST'])
@jwt_required()
def create_round():
    identity = get_jwt_identity()
    role, role_id = _parse_identity(identity)
    if role != 'parent':
        return jsonify({'error': 'Only parents can create lottery rounds'}), 403

    data = request.get_json()
    child_id = data.get('child_id')
    pity_limit = data.get('pity_limit')
    prizes_data = data.get('prizes', [])

    if not child_id or pity_limit is None or not prizes_data:
        return jsonify({'error': 'Missing required fields'}), 400

    if int(pity_limit) < 1:
        return jsonify({'error': 'pity_limit must be at least 1'}), 400

    child = Child.query.get(child_id)
    if not child or child.parent_id != role_id:
        return jsonify({'error': 'Child not found'}), 404

    # Validate prizes
    jackpot_count = sum(1 for p in prizes_data if p.get('is_jackpot'))
    if jackpot_count != 1:
        return jsonify({'error': 'Exactly one prize must be the jackpot'}), 400

    prob_sum = sum(int(p.get('probability', 0)) for p in prizes_data)
    if prob_sum != 100:
        return jsonify({'error': 'Prize probabilities must sum to 100'}), 400

    for p in prizes_data:
        prob = int(p.get('probability', 0))
        if prob < 1 or prob > 99:
            return jsonify({'error': 'Each prize probability must be between 1 and 99'}), 400

    # No duplicate active round
    existing = LotteryRound.query.filter_by(
        child_id=child_id, status='active', mode=MODE_RANDOM).first()
    if existing:
        return jsonify({'error': 'Child already has an active lottery round'}), 400

    rnd = LotteryRound(
        parent_id=role_id,
        child_id=child_id,
        mode=MODE_RANDOM,
        pity_limit=int(pity_limit),
    )
    db.session.add(rnd)
    db.session.flush()  # get rnd.id

    for p in prizes_data:
        prize = LotteryPrize(
            round_id=rnd.id,
            name=p['name'],
            probability=int(p['probability']),
            is_jackpot=bool(p.get('is_jackpot', False)),
        )
        db.session.add(prize)

    db.session.commit()
    return jsonify(_round_to_dict(rnd)), 201


# ── POST /rounds/<id>/finish ──────────────────────────────────────────────────

@lottery_bp.route('/rounds/<int:round_id>/finish', methods=['POST'])
@jwt_required()
def finish_round(round_id):
    identity = get_jwt_identity()
    role, role_id = _parse_identity(identity)
    if role != 'parent':
        return jsonify({'error': 'Only parents can finish lottery rounds'}), 403

    rnd = LotteryRound.query.get(round_id)
    if not rnd or rnd.parent_id != role_id or rnd.mode != MODE_RANDOM:
        return jsonify({'error': 'Round not found'}), 404

    if rnd.status == 'finished':
        return jsonify({'error': 'Round is already finished'}), 400

    rnd.status = 'finished'
    rnd.finished_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_round_to_dict(rnd)), 200


# ── GET /rounds?child_id= ─────────────────────────────────────────────────────

@lottery_bp.route('/rounds', methods=['GET'])
@jwt_required()
def list_rounds():
    identity = get_jwt_identity()
    role, role_id = _parse_identity(identity)
    if role != 'parent':
        return jsonify({'error': 'Only parents can list rounds'}), 403

    child_id = request.args.get('child_id')
    if not child_id:
        return jsonify({'error': 'child_id query param required'}), 400

    child = Child.query.get(child_id)
    if not child or child.parent_id != role_id:
        return jsonify({'error': 'Child not found'}), 404

    rounds = (
        LotteryRound.query
        .filter_by(child_id=child_id, mode=MODE_RANDOM)
        .order_by(LotteryRound.created_at.desc())
        .all()
    )
    return jsonify({'rounds': [_round_to_dict(r) for r in rounds]}), 200


# ── GET /active?child_id= ─────────────────────────────────────────────────────

@lottery_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_round():
    identity = get_jwt_identity()
    role, role_id = _parse_identity(identity)

    child_id = request.args.get('child_id')
    if not child_id:
        return jsonify({'error': 'child_id query param required'}), 400

    _, err = check_child_access(role, role_id, child_id)
    if err:
        return err

    rnd = LotteryRound.query.filter_by(
        child_id=child_id, status='active', mode=MODE_RANDOM).first()
    if not rnd:
        return jsonify({'active': False}), 200

    return jsonify({'active': True, 'round': _round_to_dict(rnd)}), 200


# ── POST /draw ────────────────────────────────────────────────────────────────

@lottery_bp.route('/draw', methods=['POST'])
@jwt_required()
def draw():
    identity = get_jwt_identity()
    role, role_id = _parse_identity(identity)
    if role != 'child':
        return jsonify({'error': 'Only children can draw'}), 403

    child_id = role_id
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    data = request.get_json()
    tickets = data.get('tickets')
    if tickets is None or int(tickets) < 1:
        return jsonify({'error': 'tickets must be at least 1'}), 400
    tickets = int(tickets)

    rnd = LotteryRound.query.filter_by(
        child_id=child_id, status='active', mode=MODE_RANDOM).first()
    if not rnd:
        return jsonify({'error': 'No active lottery round'}), 400

    if child.lottery_tickets < tickets:
        return jsonify({'error': 'Insufficient lottery tickets', 'lottery_tickets': child.lottery_tickets}), 400

    prizes = LotteryPrize.query.filter_by(round_id=rnd.id).all()
    slots = _build_slots(prizes)
    jackpot_prize = next(p for p in prizes if p.is_jackpot)

    results = []
    for i in range(tickets):
        current_draw_index = rnd.draws_used + 1
        will_hit_pity = (
            not rnd.jackpot_hit
            and current_draw_index >= rnd.pity_limit
        )

        chosen = jackpot_prize if will_hit_pity else random.choice(slots)

        draw_result = LotteryDrawResult(
            round_id=rnd.id,
            child_id=child_id,
            prize_id=chosen.id,
            prize_name=chosen.name,
            is_jackpot=chosen.is_jackpot,
            is_pity=will_hit_pity,
            draw_index=current_draw_index,
        )
        db.session.add(draw_result)
        db.session.flush()  # get draw_result.id for FK

        award_prize_to_child(rnd.parent_id, child_id, chosen.name, draw_result.id)

        results.append({
            'draw_index': current_draw_index,
            'prize_name': chosen.name,
            'is_jackpot': chosen.is_jackpot,
            'is_pity': will_hit_pity,
        })

        rnd.draws_used += 1

        if chosen.is_jackpot:
            rnd.jackpot_hit = True
            rnd.status = 'finished'
            rnd.finished_at = datetime.utcnow()
            break

    tickets_used = len(results)
    child.lottery_tickets -= tickets_used
    db.session.commit()

    return jsonify({
        'tickets_used': tickets_used,
        'remaining_tickets': child.lottery_tickets,
        'results': results,
        'round_status': rnd.status,
        'draws_until_pity': max(0, rnd.pity_limit - rnd.draws_used),
    }), 200


# ── GET /history?child_id= ────────────────────────────────────────────────────

@lottery_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    identity = get_jwt_identity()
    role, role_id = _parse_identity(identity)

    child_id = request.args.get('child_id')
    if not child_id:
        return jsonify({'error': 'child_id query param required'}), 400

    _, err = check_child_access(role, role_id, child_id)
    if err:
        return err

    results = (
        LotteryDrawResult.query
        .join(LotteryRound, LotteryDrawResult.round_id == LotteryRound.id)
        .filter(LotteryDrawResult.child_id == child_id, LotteryRound.mode == MODE_RANDOM)
        .order_by(LotteryDrawResult.created_at.desc())
        .all()
    )

    return jsonify({
        'child_id': child_id,
        'results': [
            {
                'id': r.id,
                'round_id': r.round_id,
                'prize_name': r.prize_name,
                'is_jackpot': r.is_jackpot,
                'is_pity': r.is_pity,
                'draw_index': r.draw_index,
                'redeemed': r.redeemed,
                'redeemed_at': r.redeemed_at.isoformat() + 'Z' if r.redeemed_at else None,
                'created_at': r.created_at.isoformat() + 'Z',
            }
            for r in results
        ]
    }), 200
