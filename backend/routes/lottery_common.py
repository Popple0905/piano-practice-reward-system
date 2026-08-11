"""Helpers shared by the classic lottery (`lottery.py`) and Ichiban Kuji (`ichiban.py`).

Both features live on the same `lottery_*` tables, distinguished by `LotteryRound.mode`,
and hand out prizes through the same SpecialRedemption pipeline.
"""
from models import db, Child, SpecialRedemption

MODE_RANDOM = 'random'
MODE_ICHIBAN = 'ichiban'


def parse_identity(identity):
    """Return (role, id_value). role is 'parent' or 'child', or (None, None) if unrecognised."""
    if identity.startswith('parent_'):
        return 'parent', int(identity.split('_')[1])
    if identity.startswith('child_'):
        return 'child', identity.split('_', 1)[1]
    return None, None


def check_child_access(role, role_id, child_id):
    """Verify the caller may act on `child_id`.

    Returns (child_or_None, error_response_or_None). A parent must own the child;
    a child may only reach itself.
    """
    from flask import jsonify

    if role == 'parent':
        child = Child.query.get(child_id)
        if not child or child.parent_id != role_id:
            return None, (jsonify({'error': 'Child not found'}), 404)
        return child, None

    if role == 'child':
        if role_id != child_id:
            return None, (jsonify({'error': 'Permission denied'}), 403)
        child = Child.query.get(child_id)
        if not child:
            return None, (jsonify({'error': 'Child not found'}), 404)
        return child, None

    return None, (jsonify({'error': 'Invalid token'}), 401)


def award_prize_to_child(parent_id, child_id, display_name, draw_result_id):
    """Put a won prize into the child's special-redemption list.

    Aggregates into an existing lottery-sourced item of the same name (bumping its
    quantity) instead of creating a duplicate row; otherwise creates a new one.
    """
    existing = SpecialRedemption.query.filter(
        SpecialRedemption.child_id == child_id,
        SpecialRedemption.content == display_name,
        SpecialRedemption.points_cost == 0,
        SpecialRedemption.lottery_draw_result_id.isnot(None),
    ).first()

    if existing is not None:
        existing.quantity = (existing.quantity or 0) + 1
        return existing

    item = SpecialRedemption(
        parent_id=parent_id,
        child_id=child_id,
        content=display_name,
        points_cost=0,
        quantity=1,
        lottery_draw_result_id=draw_result_id,
    )
    db.session.add(item)
    return item
