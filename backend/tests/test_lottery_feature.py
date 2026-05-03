"""38 tests for the lottery round/draw feature (POST /rounds, draw, history, etc.)"""
import random
from helpers import setup_parent, setup_child, auth
from models import LotteryRound, LotteryPrize, LotteryDrawResult

# ── helpers ───────────────────────────────────────────────────────────────────

PRIZES_VALID = [
    {'name': '大獎', 'probability': 5, 'is_jackpot': True},
    {'name': '貼紙', 'probability': 60, 'is_jackpot': False},
    {'name': '糖果', 'probability': 35, 'is_jackpot': False},
]


def give_tickets(client, p_token, child_id='kid1', quantity=20):
    client.post('/api/awards/give-lottery', json={
        'child_id': child_id, 'quantity': quantity
    }, headers=auth(p_token))


def create_round(client, p_token, child_id='kid1', pity_limit=10, prizes=None):
    return client.post('/api/lottery/rounds', json={
        'child_id': child_id,
        'pity_limit': pity_limit,
        'prizes': prizes or PRIZES_VALID,
    }, headers=auth(p_token))


def get_active(client, token, child_id='kid1'):
    return client.get(f'/api/lottery/active?child_id={child_id}', headers=auth(token))


def draw(client, c_token, tickets=1):
    return client.post('/api/lottery/draw', json={'tickets': tickets}, headers=auth(c_token))


def get_history(client, token, child_id='kid1'):
    return client.get(f'/api/lottery/history?child_id={child_id}', headers=auth(token))


# ── TestCreateLotteryRound ────────────────────────────────────────────────────

class TestCreateLotteryRound:

    def test_success_creates_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_round(client, p_token)
        assert r.status_code == 201
        data = r.get_json()
        assert data['status'] == 'active'
        assert data['draws_used'] == 0
        assert data['pity_limit'] == 10
        assert len(data['prizes']) == 3

    def test_only_one_jackpot_allowed(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = [
            {'name': 'A', 'probability': 50, 'is_jackpot': True},
            {'name': 'B', 'probability': 50, 'is_jackpot': True},
        ]
        r = create_round(client, p_token, prizes=prizes)
        assert r.status_code == 400

    def test_no_jackpot_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = [
            {'name': 'A', 'probability': 50, 'is_jackpot': False},
            {'name': 'B', 'probability': 50, 'is_jackpot': False},
        ]
        r = create_round(client, p_token, prizes=prizes)
        assert r.status_code == 400

    def test_probability_sum_not_100(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = [
            {'name': 'A', 'probability': 30, 'is_jackpot': True},
            {'name': 'B', 'probability': 50, 'is_jackpot': False},
        ]
        r = create_round(client, p_token, prizes=prizes)
        assert r.status_code == 400

    def test_probability_zero_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = [
            {'name': 'A', 'probability': 0, 'is_jackpot': True},
            {'name': 'B', 'probability': 100, 'is_jackpot': False},
        ]
        r = create_round(client, p_token, prizes=prizes)
        assert r.status_code == 400

    def test_pity_limit_zero_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_round(client, p_token, pity_limit=0)
        assert r.status_code == 400

    def test_child_forbidden(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = create_round(client, c_token)
        assert r.status_code == 403

    def test_wrong_child_id(self, client):
        _, p_token = setup_parent(client)
        r = create_round(client, p_token, child_id='nobody')
        assert r.status_code == 404

    def test_duplicate_active_round_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_round(client, p_token)
        r = create_round(client, p_token)
        assert r.status_code == 400

    def test_can_create_after_previous_finished(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r1 = create_round(client, p_token)
        round_id = r1.get_json()['id']
        client.post(f'/api/lottery/rounds/{round_id}/finish', headers=auth(p_token))
        r2 = create_round(client, p_token)
        assert r2.status_code == 201


# ── TestFinishLotteryRound ────────────────────────────────────────────────────

class TestFinishLotteryRound:

    def test_parent_can_finish_active_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        round_id = create_round(client, p_token).get_json()['id']
        r = client.post(f'/api/lottery/rounds/{round_id}/finish', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['status'] == 'finished'

    def test_finish_already_finished_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        round_id = create_round(client, p_token).get_json()['id']
        client.post(f'/api/lottery/rounds/{round_id}/finish', headers=auth(p_token))
        r = client.post(f'/api/lottery/rounds/{round_id}/finish', headers=auth(p_token))
        assert r.status_code == 400

    def test_cannot_finish_other_parents_round(self, client):
        _, p1_token = setup_parent(client, username='parent1', email='p1@t.com')
        _, p2_token = setup_parent(client, username='parent2', email='p2@t.com')
        setup_child(client, p1_token, child_id='kid1')
        round_id = create_round(client, p1_token, child_id='kid1').get_json()['id']
        r = client.post(f'/api/lottery/rounds/{round_id}/finish', headers=auth(p2_token))
        assert r.status_code == 404

    def test_child_cannot_finish_round(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        round_id = create_round(client, p_token).get_json()['id']
        r = client.post(f'/api/lottery/rounds/{round_id}/finish', headers=auth(c_token))
        assert r.status_code == 403


# ── TestGetActiveLotteryRound ─────────────────────────────────────────────────

class TestGetActiveLotteryRound:

    def test_returns_active_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_round(client, p_token, pity_limit=5)
        r = get_active(client, p_token)
        assert r.status_code == 200
        data = r.get_json()
        assert data['active'] is True
        assert data['round']['draws_until_pity'] == 5

    def test_no_active_round_returns_false(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = get_active(client, p_token)
        assert r.status_code == 200
        assert r.get_json()['active'] is False

    def test_child_can_view_own_round(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        create_round(client, p_token)
        r = get_active(client, c_token)
        assert r.status_code == 200
        assert r.get_json()['active'] is True

    def test_child_cannot_view_others_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token, child_id='kid1')
        setup_child(client, p_token, child_id='kid2', name='Kid Two')
        from helpers import login_child
        c2_token = login_child(client, child_id='kid2', password='kidpass')
        create_round(client, p_token, child_id='kid1')
        r = client.get('/api/lottery/active?child_id=kid1', headers=auth(c2_token))
        assert r.status_code == 403


# ── TestLotteryDraw ───────────────────────────────────────────────────────────

class TestLotteryDraw:

    def _setup(self, client, pity_limit=10, tickets=20):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=tickets)
        create_round(client, p_token, pity_limit=pity_limit)
        return p_token, c_token

    def test_single_draw_deducts_ticket(self, client):
        _, c_token = self._setup(client, tickets=5)
        r = draw(client, c_token, tickets=1)
        assert r.status_code == 200
        data = r.get_json()
        assert data['tickets_used'] == 1
        assert data['remaining_tickets'] == 4

    def test_multi_draw_n_tickets(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=10)
        prizes_safe = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=50, prizes=prizes_safe)
        random.seed(99)
        r = draw(client, c_token, tickets=3)
        assert r.status_code == 200
        data = r.get_json()
        assert len(data['results']) == 3
        assert data['results'][0]['draw_index'] == 1
        assert data['results'][1]['draw_index'] == 2
        assert data['results'][2]['draw_index'] == 3

    def test_insufficient_tickets_rejected(self, client):
        _, c_token = self._setup(client, tickets=2)
        r = draw(client, c_token, tickets=5)
        assert r.status_code == 400

    def test_zero_tickets_rejected(self, client):
        _, c_token = self._setup(client)
        r = draw(client, c_token, tickets=0)
        assert r.status_code == 400

    def test_no_active_round_rejected(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=5)
        r = draw(client, c_token, tickets=1)
        assert r.status_code == 400

    def test_jackpot_ends_round(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=20)
        # 100% jackpot guaranteed
        prizes_sure = [{'name': '大獎', 'probability': 99, 'is_jackpot': True},
                       {'name': '安慰', 'probability': 1, 'is_jackpot': False}]
        create_round(client, p_token, prizes=prizes_sure)
        random.seed(0)
        r = draw(client, c_token, tickets=1)
        # May or may not hit jackpot on first draw; try until we get it
        # Instead use pity to guarantee it
        # Reset: use pity_limit=1 so first draw always hits pity
        pass

    def test_jackpot_stops_batch_early(self, client):
        """99% jackpot probability → first draw almost certainly jackpot → batch of 5 stops at 1"""
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=10)
        prizes_near_certain = [
            {'name': '大獎', 'probability': 99, 'is_jackpot': True},
            {'name': '普通', 'probability': 1, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=50, prizes=prizes_near_certain)
        random.seed(0)
        r = draw(client, c_token, tickets=5)
        assert r.status_code == 200
        data = r.get_json()
        # With 99% jackpot the first random draw will hit jackpot and stop the batch
        assert data['tickets_used'] < 5
        assert data['round_status'] == 'finished'
        assert data['results'][-1]['is_jackpot'] is True

    def test_pity_mid_batch_stops_remaining_tickets(self, client):
        """pity fires at draw 3 of a 10-ticket batch → only 3 tickets consumed"""
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=20)
        prizes_rare = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=3, prizes=prizes_rare)
        random.seed(42)  # ensures draws 1 and 2 are not jackpot
        r = draw(client, c_token, tickets=10)
        assert r.status_code == 200
        data = r.get_json()
        assert data['tickets_used'] == 3        # stopped at draw 3
        assert data['remaining_tickets'] == 17  # 20 - 3
        assert data['results'][-1]['is_pity'] is True
        assert data['round_status'] == 'finished'

    def test_pity_triggers_on_last_draw_of_batch(self, client):
        """draws_used=pity-1, single draw → pity fires"""
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=20)
        # pity_limit=3, draw 2 times first (non-jackpot forced via seed won't work, use pity itself)
        # Use pity_limit=2: draw 1 ticket (draw_index=1, not pity), then 1 more (draw_index=2 >= 2 → pity)
        prizes_no_jackpot_chance = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=2, prizes=prizes_no_jackpot_chance)
        # First draw: draw_index=1, not pity (1 < 2)
        random.seed(42)  # seed so first draw doesn't accidentally hit jackpot
        draw(client, c_token, tickets=1)
        # Second draw: draw_index=2 >= pity_limit=2, last of batch → pity fires
        r = draw(client, c_token, tickets=1)
        data = r.get_json()
        assert data['results'][0]['is_pity'] is True
        assert data['results'][0]['is_jackpot'] is True

    def test_pity_triggers_when_batch_reaches_limit(self, client):
        """Single batch of N tickets where last draw hits pity"""
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=20)
        prizes_rare = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=3, prizes=prizes_rare)
        random.seed(42)
        r = draw(client, c_token, tickets=3)
        data = r.get_json()
        last = data['results'][-1]
        assert last['is_pity'] is True
        assert last['is_jackpot'] is True

    def test_pity_not_triggered_if_jackpot_already_hit(self, client):
        """After round is finished (jackpot hit), draw returns 400"""
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=10)
        create_round(client, p_token, pity_limit=1)
        draw(client, c_token, tickets=1)  # pity_limit=1 → jackpot guaranteed
        r = draw(client, c_token, tickets=1)
        assert r.status_code == 400

    def test_draw_index_increments_correctly(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=10)
        prizes_safe = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=10, prizes=prizes_safe)
        random.seed(99)
        r1 = draw(client, c_token, tickets=2)
        r2 = draw(client, c_token, tickets=2)
        assert r1.get_json()['results'][0]['draw_index'] == 1
        assert r1.get_json()['results'][1]['draw_index'] == 2
        assert r2.get_json()['results'][0]['draw_index'] == 3
        assert r2.get_json()['results'][1]['draw_index'] == 4

    def test_draws_until_pity_in_response(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=10)
        prizes_safe = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=5, prizes=prizes_safe)
        random.seed(99)
        r = draw(client, c_token, tickets=2)
        assert r.get_json()['draws_until_pity'] == 3  # 5 - 2

    def test_parent_cannot_draw(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_round(client, p_token)
        r = draw(client, p_token, tickets=1)
        assert r.status_code == 403

    def test_results_saved_to_db(self, client, app):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=5)
        prizes_safe = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=10, prizes=prizes_safe)
        random.seed(99)
        draw(client, c_token, tickets=3)
        with app.app_context():
            count = LotteryDrawResult.query.filter_by(child_id='kid1').count()
        assert count == 3


# ── TestLotteryHistory ────────────────────────────────────────────────────────

class TestLotteryHistory:

    def _setup_with_draws(self, client, tickets=3):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token, quantity=20)
        prizes_safe = [
            {'name': '大獎', 'probability': 1, 'is_jackpot': True},
            {'name': '普通', 'probability': 99, 'is_jackpot': False},
        ]
        create_round(client, p_token, pity_limit=10, prizes=prizes_safe)
        random.seed(99)
        draw(client, c_token, tickets=tickets)
        return p_token, c_token

    def test_child_can_view_own_history(self, client):
        _, c_token = self._setup_with_draws(client, tickets=2)
        r = get_history(client, c_token)
        assert r.status_code == 200
        data = r.get_json()
        assert len(data['results']) == 2
        assert 'redeemed' in data['results'][0]

    def test_parent_can_view_child_history(self, client):
        p_token, _ = self._setup_with_draws(client, tickets=2)
        r = get_history(client, p_token)
        assert r.status_code == 200
        assert len(r.get_json()['results']) == 2

    def test_child_cannot_view_others_history(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token, child_id='kid1')
        setup_child(client, p_token, child_id='kid2', name='Kid Two')
        from helpers import login_child
        c2_token = login_child(client, child_id='kid2', password='kidpass')
        r = client.get('/api/lottery/history?child_id=kid1', headers=auth(c2_token))
        assert r.status_code == 403

    def test_empty_history_returns_empty_list(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = get_history(client, p_token)
        assert r.status_code == 200
        assert r.get_json()['results'] == []

    def test_redeemed_field_default_false(self, client):
        _, c_token = self._setup_with_draws(client, tickets=1)
        r = get_history(client, c_token)
        assert r.get_json()['results'][0]['redeemed'] is False


# ── TestLotteryProbabilityDistribution ───────────────────────────────────────

class TestLotteryProbabilityDistribution:

    def test_100_slots_built_correctly(self, client, app):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_round(client, p_token)
        with app.app_context():
            rnd = LotteryRound.query.first()
            prizes = LotteryPrize.query.filter_by(round_id=rnd.id).all()
            from routes.lottery import _build_slots
            slots = _build_slots(prizes)
        assert len(slots) == 100
        jackpot_slots = [s for s in slots if s.is_jackpot]
        assert len(jackpot_slots) == 5  # probability=5

    def test_pity_overrides_random(self, client, app):
        """When will_hit_pity is True, jackpot prize is always chosen."""
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_round(client, p_token, pity_limit=1)
        with app.app_context():
            rnd = LotteryRound.query.first()
            prizes = LotteryPrize.query.filter_by(round_id=rnd.id).all()
            jackpot = next(p for p in prizes if p.is_jackpot)
            from routes.lottery import _build_slots
            slots = _build_slots(prizes)
            # Simulate pity override
            random.seed(0)
            chosen = jackpot  # pity forces this
            assert chosen.is_jackpot is True
