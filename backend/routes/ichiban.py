"""Ichiban Kuji (一番賞).

Differences from the classic lottery in `lottery.py`:
  - Prize quantities are fixed; draws are without replacement (a prize that runs out
    can no longer be drawn).
  - Prizes are named by grade in order: A賞, B賞, C賞, ...
  - No jackpot and no pity counter.
  - The round only ends when every prize has been drawn (or the parent force-ends it).

It shares the `lottery_*` tables (via `LotteryRound.mode == 'ichiban'`), the
lottery-ticket balance on `Child`, and the SpecialRedemption prize pipeline.
"""
import random
import string
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Child, LotteryRound, LotteryPrize, LotteryDrawResult
from routes.lottery_common import (
    MODE_ICHIBAN, parse_identity, check_child_access, award_prize_to_child,
)

ichiban_bp = Blueprint('ichiban', __name__)

GRADES = string.ascii_uppercase  # A–Z, so at most 26 prize grades per round
MAX_PRIZES = len(GRADES)


def _display_name(grade, name):
    """The label a child sees for a won prize, e.g. 'A賞：去遊樂園'."""
    return f'{grade}賞：{name}'


def _round_to_dict(rnd, include_prizes=True):
    remaining = max(0, (rnd.total_draws or 0) - (rnd.draws_used or 0))
    data = {
        'id': rnd.id,
        'child_id': rnd.child_id,
        'parent_id': rnd.parent_id,
        'mode': rnd.mode,
        'total_draws': rnd.total_draws or 0,
        'draws_used': rnd.draws_used or 0,
        'remaining_draws': remaining,
        'status': rnd.status,
        'created_at': rnd.created_at.isoformat() + 'Z',
        'finished_at': rnd.finished_at.isoformat() + 'Z' if rnd.finished_at else None,
    }
    if include_prizes:
        prizes = sorted(rnd.prizes, key=lambda p: p.grade or '')
        data['prizes'] = [
            {
                'id': p.id,
                'grade': p.grade,
                'name': p.name,
                'display_name': _display_name(p.grade, p.name),
                'total_quantity': p.total_quantity,
                'remaining_quantity': p.remaining_quantity,
            }
            for p in prizes
        ]
    return data


# ── POST /rounds ──────────────────────────────────────────────────────────────

@ichiban_bp.route('/rounds', methods=['POST'])
@jwt_required()
def create_round():
    """Parent sets up a new Ichiban Kuji box for a child.

    Body: {child_id, prizes: [{name, quantity}, ...]} — grades are assigned A, B, C…
    following the order of the list.
    """
    identity = get_jwt_identity()
    role, role_id = parse_identity(identity)
    if role != 'parent':
        return jsonify({'error': 'Only parents can create ichiban rounds'}), 403

    data = request.get_json() or {}
    child_id = data.get('child_id')
    prizes_data = data.get('prizes', [])

    if not child_id or not prizes_data:
        return jsonify({'error': 'Missing required fields'}), 400

    if len(prizes_data) > MAX_PRIZES:
        return jsonify({'error': f'At most {MAX_PRIZES} prize grades are allowed'}), 400

    child = Child.query.get(child_id)
    if not child or child.parent_id != role_id:
        return jsonify({'error': 'Child not found'}), 404

    # Validate every prize before writing anything
    cleaned = []
    for p in prizes_data:
        name = (p.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'Each prize must have a name'}), 400
        try:
            quantity = int(p.get('quantity', 0))
        except (TypeError, ValueError):
            return jsonify({'error': 'Prize quantity must be a number'}), 400
        if quantity < 1:
            return jsonify({'error': 'Each prize quantity must be at least 1'}), 400
        cleaned.append((name, quantity))

    existing = LotteryRound.query.filter_by(
        child_id=child_id, status='active', mode=MODE_ICHIBAN).first()
    if existing:
        return jsonify({'error': 'Child already has an active ichiban round'}), 400

    rnd = LotteryRound(
        parent_id=role_id,
        child_id=child_id,
        mode=MODE_ICHIBAN,
        pity_limit=0,          # not applicable in ichiban mode
        total_draws=sum(q for _, q in cleaned),
    )
    db.session.add(rnd)
    db.session.flush()  # get rnd.id

    for index, (name, quantity) in enumerate(cleaned):
        db.session.add(LotteryPrize(
            round_id=rnd.id,
            name=name,
            probability=0,     # not applicable in ichiban mode
            is_jackpot=False,
            grade=GRADES[index],
            total_quantity=quantity,
            remaining_quantity=quantity,
        ))

    db.session.commit()
    return jsonify(_round_to_dict(rnd)), 201


# ── POST /rounds/<id>/finish ──────────────────────────────────────────────────

@ichiban_bp.route('/rounds/<int:round_id>/finish', methods=['POST'])
@jwt_required()
def finish_round(round_id):
    """Parent force-ends a round before every prize has been drawn."""
    identity = get_jwt_identity()
    role, role_id = parse_identity(identity)
    if role != 'parent':
        return jsonify({'error': 'Only parents can finish ichiban rounds'}), 403

    rnd = LotteryRound.query.get(round_id)
    if not rnd or rnd.parent_id != role_id or rnd.mode != MODE_ICHIBAN:
        return jsonify({'error': 'Round not found'}), 404

    if rnd.status == 'finished':
        return jsonify({'error': 'Round is already finished'}), 400

    rnd.status = 'finished'
    rnd.finished_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_round_to_dict(rnd)), 200


# ── GET /rounds?child_id= ─────────────────────────────────────────────────────

@ichiban_bp.route('/rounds', methods=['GET'])
@jwt_required()
def list_rounds():
    identity = get_jwt_identity()
    role, role_id = parse_identity(identity)
    if role != 'parent':
        return jsonify({'error': 'Only parents can list rounds'}), 403

    child_id = request.args.get('child_id')
    if not child_id:
        return jsonify({'error': 'child_id query param required'}), 400

    _, err = check_child_access(role, role_id, child_id)
    if err:
        return err

    rounds = (
        LotteryRound.query
        .filter_by(child_id=child_id, mode=MODE_ICHIBAN)
        .order_by(LotteryRound.created_at.desc())
        .all()
    )
    return jsonify({'rounds': [_round_to_dict(r) for r in rounds]}), 200


# ── GET /active?child_id= ─────────────────────────────────────────────────────

@ichiban_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_round():
    identity = get_jwt_identity()
    role, role_id = parse_identity(identity)

    child_id = request.args.get('child_id')
    if not child_id:
        return jsonify({'error': 'child_id query param required'}), 400

    _, err = check_child_access(role, role_id, child_id)
    if err:
        return err

    rnd = LotteryRound.query.filter_by(
        child_id=child_id, status='active', mode=MODE_ICHIBAN).first()
    if not rnd:
        return jsonify({'active': False}), 200

    return jsonify({'active': True, 'round': _round_to_dict(rnd)}), 200


# ── POST /draw ────────────────────────────────────────────────────────────────

@ichiban_bp.route('/draw', methods=['POST'])
@jwt_required()
def draw():
    """Child draws `tickets` prizes without replacement from its active box."""
    identity = get_jwt_identity()
    role, role_id = parse_identity(identity)
    if role != 'child':
        return jsonify({'error': 'Only children can draw'}), 403

    child_id = role_id
    child = Child.query.get(child_id)
    if not child:
        return jsonify({'error': 'Child not found'}), 404

    data = request.get_json() or {}
    tickets = data.get('tickets')
    if tickets is None or int(tickets) < 1:
        return jsonify({'error': 'tickets must be at least 1'}), 400
    tickets = int(tickets)

    rnd = LotteryRound.query.filter_by(
        child_id=child_id, status='active', mode=MODE_ICHIBAN).first()
    if not rnd:
        return jsonify({'error': 'No active ichiban round'}), 400

    if child.lottery_tickets < tickets:
        return jsonify({
            'error': 'Insufficient lottery tickets',
            'lottery_tickets': child.lottery_tickets,
        }), 400

    prizes = LotteryPrize.query.filter_by(round_id=rnd.id).all()
    remaining_draws = sum(p.remaining_quantity or 0 for p in prizes)
    if tickets > remaining_draws:
        return jsonify({
            'error': 'Not enough prizes left in this round',
            'remaining_draws': remaining_draws,
        }), 400

    results = []
    for _ in range(tickets):
        # Draw without replacement: every remaining prize copy is one equally likely slot.
        pool = [p for p in prizes for _ in range(p.remaining_quantity or 0)]
        chosen = random.choice(pool)
        chosen.remaining_quantity -= 1
        rnd.draws_used += 1

        draw_result = LotteryDrawResult(
            round_id=rnd.id,
            child_id=child_id,
            prize_id=chosen.id,
            prize_name=chosen.name,
            is_jackpot=False,
            is_pity=False,
            grade=chosen.grade,
            draw_index=rnd.draws_used,
        )
        db.session.add(draw_result)
        db.session.flush()  # get draw_result.id for the FK below

        award_prize_to_child(
            rnd.parent_id, child_id, _display_name(chosen.grade, chosen.name), draw_result.id)

        results.append({
            'draw_index': draw_result.draw_index,
            'grade': chosen.grade,
            'prize_name': chosen.name,
            'display_name': _display_name(chosen.grade, chosen.name),
        })

    remaining_draws -= tickets
    if remaining_draws == 0:
        rnd.status = 'finished'
        rnd.finished_at = datetime.utcnow()

    child.lottery_tickets -= tickets
    db.session.commit()

    return jsonify({
        'tickets_used': tickets,
        'remaining_tickets': child.lottery_tickets,
        'results': results,
        'round_status': rnd.status,
        'remaining_draws': remaining_draws,
        'prizes': _round_to_dict(rnd)['prizes'],
    }), 200


# ── GET /history?child_id= ────────────────────────────────────────────────────

@ichiban_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    identity = get_jwt_identity()
    role, role_id = parse_identity(identity)

    child_id = request.args.get('child_id')
    if not child_id:
        return jsonify({'error': 'child_id query param required'}), 400

    _, err = check_child_access(role, role_id, child_id)
    if err:
        return err

    results = (
        LotteryDrawResult.query
        .join(LotteryRound, LotteryDrawResult.round_id == LotteryRound.id)
        .filter(LotteryDrawResult.child_id == child_id, LotteryRound.mode == MODE_ICHIBAN)
        .order_by(LotteryDrawResult.created_at.desc(), LotteryDrawResult.id.desc())
        .all()
    )

    return jsonify({
        'child_id': child_id,
        'results': [
            {
                'id': r.id,
                'round_id': r.round_id,
                'grade': r.grade,
                'prize_name': r.prize_name,
                'display_name': _display_name(r.grade, r.prize_name),
                'draw_index': r.draw_index,
                'redeemed': r.redeemed,
                'redeemed_at': r.redeemed_at.isoformat() + 'Z' if r.redeemed_at else None,
                'created_at': r.created_at.isoformat() + 'Z',
            }
            for r in results
        ]
    }), 200
