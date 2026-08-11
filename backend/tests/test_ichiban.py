"""Tests for the Ichiban Kuji (一番賞) feature — /api/ichiban."""
from collections import Counter

from helpers import setup_parent, setup_child, auth
from models import LotteryRound, LotteryPrize, LotteryDrawResult, SpecialRedemption

# ── helpers ───────────────────────────────────────────────────────────────────

PRIZES_VALID = [
    {'name': '去遊樂園', 'quantity': 1},
    {'name': '吃冰淇淋', 'quantity': 3},
    {'name': '多玩30分鐘', 'quantity': 6},
]
TOTAL_DRAWS = 10


def give_tickets(client, p_token, child_id='kid1', quantity=30):
    return client.post('/api/awards/give-lottery', json={
        'child_id': child_id, 'quantity': quantity
    }, headers=auth(p_token))


def create_round(client, p_token, child_id='kid1', prizes=None):
    return client.post('/api/ichiban/rounds', json={
        'child_id': child_id,
        'prizes': PRIZES_VALID if prizes is None else prizes,
    }, headers=auth(p_token))


def get_active(client, token, child_id='kid1'):
    return client.get(f'/api/ichiban/active?child_id={child_id}', headers=auth(token))


def draw(client, c_token, tickets=1):
    return client.post('/api/ichiban/draw', json={'tickets': tickets}, headers=auth(c_token))


def get_history(client, token, child_id='kid1'):
    return client.get(f'/api/ichiban/history?child_id={child_id}', headers=auth(token))


def setup_round(client, tickets=30):
    """Parent + child + an active round, with tickets granted. Returns (p_token, c_token)."""
    _, p_token = setup_parent(client)
    c_token = setup_child(client, p_token)
    give_tickets(client, p_token, quantity=tickets)
    create_round(client, p_token)
    return p_token, c_token


# ── TestCreateRound ───────────────────────────────────────────────────────────

class TestCreateRound:

    def test_success_creates_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_round(client, p_token)
        assert r.status_code == 201
        data = r.get_json()
        assert data['mode'] == 'ichiban'
        assert data['status'] == 'active'
        assert data['total_draws'] == TOTAL_DRAWS
        assert data['draws_used'] == 0
        assert data['remaining_draws'] == TOTAL_DRAWS

    def test_grades_assigned_in_order(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = create_round(client, p_token).get_json()['prizes']
        assert [p['grade'] for p in prizes] == ['A', 'B', 'C']
        assert [p['name'] for p in prizes] == ['去遊樂園', '吃冰淇淋', '多玩30分鐘']
        assert prizes[0]['display_name'] == 'A賞：去遊樂園'

    def test_quantities_stored(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = create_round(client, p_token).get_json()['prizes']
        assert [p['total_quantity'] for p in prizes] == [1, 3, 6]
        assert [p['remaining_quantity'] for p in prizes] == [1, 3, 6]

    def test_child_cannot_create(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.post('/api/ichiban/rounds', json={
            'child_id': 'kid1', 'prizes': PRIZES_VALID
        }, headers=auth(c_token))
        assert r.status_code == 403

    def test_missing_prizes_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_round(client, p_token, prizes=[])
        assert r.status_code == 400

    def test_zero_quantity_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_round(client, p_token, prizes=[{'name': 'A', 'quantity': 0}])
        assert r.status_code == 400

    def test_negative_quantity_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_round(client, p_token, prizes=[{'name': 'A', 'quantity': -2}])
        assert r.status_code == 400

    def test_blank_name_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_round(client, p_token, prizes=[{'name': '   ', 'quantity': 1}])
        assert r.status_code == 400

    def test_more_than_26_grades_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = [{'name': f'獎品{i}', 'quantity': 1} for i in range(27)]
        r = create_round(client, p_token, prizes=prizes)
        assert r.status_code == 400

    def test_exactly_26_grades_allowed(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        prizes = [{'name': f'獎品{i}', 'quantity': 1} for i in range(26)]
        r = create_round(client, p_token, prizes=prizes)
        assert r.status_code == 201
        assert r.get_json()['prizes'][-1]['grade'] == 'Z'

    def test_duplicate_active_round_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_round(client, p_token)
        r = create_round(client, p_token)
        assert r.status_code == 400

    def test_other_parents_child_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        _, other_token = setup_parent(client, 'parent2', 'pass1234', 'p2@test.com')
        r = create_round(client, other_token)
        assert r.status_code == 404

    def test_nothing_written_when_validation_fails(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_round(client, p_token, prizes=[
            {'name': '好獎', 'quantity': 2},
            {'name': '壞獎', 'quantity': 0},   # invalid — whole request must be rejected
        ])
        assert LotteryRound.query.count() == 0
        assert LotteryPrize.query.count() == 0


# ── TestActiveRound ───────────────────────────────────────────────────────────

class TestActiveRound:

    def test_no_active_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        assert get_active(client, p_token).get_json()['active'] is False

    def test_parent_sees_active_round(self, client):
        p_token, _ = setup_round(client)
        data = get_active(client, p_token).get_json()
        assert data['active'] is True
        assert data['round']['total_draws'] == TOTAL_DRAWS

    def test_child_sees_active_round(self, client):
        _, c_token = setup_round(client)
        data = get_active(client, c_token).get_json()
        assert data['active'] is True
        assert len(data['round']['prizes']) == 3

    def test_other_child_denied(self, client):
        p_token, _ = setup_round(client)
        other_token = setup_child(client, p_token, 'kid2', 'Kid Two')
        r = get_active(client, other_token, 'kid1')
        assert r.status_code == 403

    def test_other_parent_denied(self, client):
        setup_round(client)
        _, other_token = setup_parent(client, 'parent2', 'pass1234', 'p2@test.com')
        assert get_active(client, other_token).status_code == 404

    def test_child_id_required(self, client):
        p_token, _ = setup_round(client)
        assert client.get('/api/ichiban/active', headers=auth(p_token)).status_code == 400


# ── TestDraw ──────────────────────────────────────────────────────────────────

class TestDraw:

    def test_single_draw_succeeds(self, client):
        _, c_token = setup_round(client)
        r = draw(client, c_token)
        assert r.status_code == 200
        data = r.get_json()
        assert data['tickets_used'] == 1
        assert len(data['results']) == 1
        assert data['results'][0]['grade'] in ('A', 'B', 'C')
        assert data['remaining_draws'] == TOTAL_DRAWS - 1

    def test_ticket_deducted(self, client):
        _, c_token = setup_round(client, tickets=5)
        assert draw(client, c_token, 2).get_json()['remaining_tickets'] == 3

    def test_multi_draw(self, client):
        _, c_token = setup_round(client)
        data = draw(client, c_token, 4).get_json()
        assert data['tickets_used'] == 4
        assert len(data['results']) == 4
        assert [r['draw_index'] for r in data['results']] == [1, 2, 3, 4]

    def test_parent_cannot_draw(self, client):
        p_token, _ = setup_round(client)
        r = client.post('/api/ichiban/draw', json={'tickets': 1}, headers=auth(p_token))
        assert r.status_code == 403

    def test_no_active_round(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token)
        assert draw(client, c_token).status_code == 400

    def test_insufficient_tickets(self, client):
        _, c_token = setup_round(client, tickets=1)
        r = draw(client, c_token, 2)
        assert r.status_code == 400
        assert 'Insufficient' in r.get_json()['error']

    def test_zero_tickets_rejected(self, client):
        _, c_token = setup_round(client)
        assert draw(client, c_token, 0).status_code == 400

    def test_cannot_draw_more_than_remaining(self, client):
        _, c_token = setup_round(client, tickets=30)
        r = draw(client, c_token, TOTAL_DRAWS + 1)
        assert r.status_code == 400
        assert r.get_json()['remaining_draws'] == TOTAL_DRAWS

    def test_no_tickets_spent_on_rejected_draw(self, client):
        _, c_token = setup_round(client, tickets=30)
        draw(client, c_token, TOTAL_DRAWS + 1)
        assert get_active(client, c_token).get_json()['round']['draws_used'] == 0

    def test_prize_remaining_decrements(self, client):
        _, c_token = setup_round(client)
        prizes = draw(client, c_token, 3).get_json()['prizes']
        assert sum(p['remaining_quantity'] for p in prizes) == TOTAL_DRAWS - 3

    def test_draws_without_replacement_exhausts_box_exactly(self, client):
        """Drawing the whole box must yield each prize exactly its configured quantity."""
        _, c_token = setup_round(client)
        won = Counter()
        for _ in range(TOTAL_DRAWS):
            won[draw(client, c_token).get_json()['results'][0]['grade']] += 1
        assert won == Counter({'A': 1, 'B': 3, 'C': 6})

    def test_multi_draw_also_exhausts_box_exactly(self, client):
        _, c_token = setup_round(client)
        results = draw(client, c_token, TOTAL_DRAWS).get_json()['results']
        assert Counter(r['grade'] for r in results) == Counter({'A': 1, 'B': 3, 'C': 6})

    def test_round_auto_finishes_when_box_empty(self, client):
        _, c_token = setup_round(client)
        data = draw(client, c_token, TOTAL_DRAWS).get_json()
        assert data['round_status'] == 'finished'
        assert data['remaining_draws'] == 0
        assert get_active(client, c_token).get_json()['active'] is False

    def test_cannot_draw_after_box_empty(self, client):
        _, c_token = setup_round(client)
        draw(client, c_token, TOTAL_DRAWS)
        assert draw(client, c_token).status_code == 400

    def test_new_round_allowed_after_box_empty(self, client):
        p_token, c_token = setup_round(client)
        draw(client, c_token, TOTAL_DRAWS)
        assert create_round(client, p_token).status_code == 201

    def test_single_prize_box(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token)
        create_round(client, p_token, prizes=[{'name': '獨獎', 'quantity': 1}])
        data = draw(client, c_token).get_json()
        assert data['results'][0]['display_name'] == 'A賞：獨獎'
        assert data['round_status'] == 'finished'


# ── TestPrizeDelivery ─────────────────────────────────────────────────────────

class TestPrizeDelivery:

    def test_prize_appears_in_special_redemptions(self, client):
        _, c_token = setup_round(client)
        name = draw(client, c_token).get_json()['results'][0]['display_name']
        items = client.get('/api/special-redemptions/child/kid1',
                           headers=auth(c_token)).get_json()['items']
        match = [i for i in items if i['content'] == name]
        assert len(match) == 1
        assert match[0]['points_cost'] == 0
        assert match[0]['from_lottery'] is True

    def test_display_name_includes_grade(self, client):
        _, c_token = setup_round(client)
        draw(client, c_token, TOTAL_DRAWS)
        items = client.get('/api/special-redemptions/child/kid1',
                           headers=auth(c_token)).get_json()['items']
        assert all(i['content'][1:2] == '賞' for i in items)

    def test_duplicate_prizes_aggregate_into_one_item(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token)
        create_round(client, p_token, prizes=[{'name': '貼紙', 'quantity': 4}])
        draw(client, c_token, 4)
        items = client.get('/api/special-redemptions/child/kid1',
                           headers=auth(c_token)).get_json()['items']
        assert len(items) == 1
        assert items[0]['quantity'] == 4

    def test_redeeming_marks_draw_result(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token)
        create_round(client, p_token, prizes=[{'name': '貼紙', 'quantity': 1}])
        draw(client, c_token)
        item = client.get('/api/special-redemptions/child/kid1',
                          headers=auth(c_token)).get_json()['items'][0]
        assert client.post(f"/api/special-redemptions/{item['id']}/redeem",
                           headers=auth(c_token)).status_code == 200
        assert get_history(client, c_token).get_json()['results'][0]['redeemed'] is True

    def test_prize_costs_no_reward_points(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token)
        create_round(client, p_token, prizes=[{'name': '貼紙', 'quantity': 1}])
        draw(client, c_token)
        item = client.get('/api/special-redemptions/child/kid1',
                          headers=auth(c_token)).get_json()['items'][0]
        client.post(f"/api/special-redemptions/{item['id']}/redeem", headers=auth(c_token))
        balance = client.get('/api/awards/balance/kid1', headers=auth(c_token)).get_json()
        assert balance['game_balance'] == 0


# ── TestFinishRound ───────────────────────────────────────────────────────────

class TestFinishRound:

    def test_parent_can_force_finish(self, client):
        p_token, c_token = setup_round(client)
        draw(client, c_token, 2)
        round_id = get_active(client, p_token).get_json()['round']['id']
        r = client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['status'] == 'finished'
        assert get_active(client, p_token).get_json()['active'] is False

    def test_child_cannot_finish(self, client):
        p_token, c_token = setup_round(client)
        round_id = get_active(client, p_token).get_json()['round']['id']
        r = client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(c_token))
        assert r.status_code == 403

    def test_finishing_twice_rejected(self, client):
        p_token, _ = setup_round(client)
        round_id = get_active(client, p_token).get_json()['round']['id']
        client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(p_token))
        r = client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(p_token))
        assert r.status_code == 400

    def test_other_parent_cannot_finish(self, client):
        p_token, _ = setup_round(client)
        round_id = get_active(client, p_token).get_json()['round']['id']
        _, other_token = setup_parent(client, 'parent2', 'pass1234', 'p2@test.com')
        r = client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(other_token))
        assert r.status_code == 404

    def test_new_round_allowed_after_force_finish(self, client):
        p_token, _ = setup_round(client)
        round_id = get_active(client, p_token).get_json()['round']['id']
        client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(p_token))
        assert create_round(client, p_token).status_code == 201

    def test_list_rounds_returns_history(self, client):
        p_token, _ = setup_round(client)
        round_id = get_active(client, p_token).get_json()['round']['id']
        client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(p_token))
        create_round(client, p_token)
        rounds = client.get('/api/ichiban/rounds?child_id=kid1',
                            headers=auth(p_token)).get_json()['rounds']
        assert len(rounds) == 2
        assert all(r['mode'] == 'ichiban' for r in rounds)


# ── TestHistory ───────────────────────────────────────────────────────────────

class TestHistory:

    def test_empty_history(self, client):
        _, c_token = setup_round(client)
        assert get_history(client, c_token).get_json()['results'] == []

    def test_history_records_every_draw(self, client):
        _, c_token = setup_round(client)
        draw(client, c_token, 4)
        results = get_history(client, c_token).get_json()['results']
        assert len(results) == 4
        assert {r['draw_index'] for r in results} == {1, 2, 3, 4}

    def test_history_includes_grade_and_display_name(self, client):
        _, c_token = setup_round(client)
        draw(client, c_token)
        entry = get_history(client, c_token).get_json()['results'][0]
        assert entry['display_name'] == f"{entry['grade']}賞：{entry['prize_name']}"

    def test_parent_can_read_history(self, client):
        p_token, c_token = setup_round(client)
        draw(client, c_token, 2)
        assert len(get_history(client, p_token).get_json()['results']) == 2

    def test_other_child_denied(self, client):
        p_token, c_token = setup_round(client)
        draw(client, c_token)
        other_token = setup_child(client, p_token, 'kid2', 'Kid Two')
        assert get_history(client, other_token, 'kid1').status_code == 403


# ── TestIsolationFromClassicLottery ───────────────────────────────────────────

LOTTERY_PRIZES = [
    {'name': '大獎', 'probability': 5, 'is_jackpot': True},
    {'name': '貼紙', 'probability': 95, 'is_jackpot': False},
]


def create_lottery_round(client, p_token, child_id='kid1', pity_limit=50):
    return client.post('/api/lottery/rounds', json={
        'child_id': child_id, 'pity_limit': pity_limit, 'prizes': LOTTERY_PRIZES,
    }, headers=auth(p_token))


class TestIsolationFromClassicLottery:
    """Both features share the lottery_* tables — neither may leak into the other."""

    def test_both_rounds_can_be_active_at_once(self, client):
        p_token, _ = setup_round(client)
        assert create_lottery_round(client, p_token).status_code == 201
        assert get_active(client, p_token).get_json()['active'] is True
        assert client.get('/api/lottery/active?child_id=kid1',
                          headers=auth(p_token)).get_json()['active'] is True

    def test_ichiban_round_not_returned_by_lottery_active(self, client):
        p_token, _ = setup_round(client)
        r = client.get('/api/lottery/active?child_id=kid1', headers=auth(p_token))
        assert r.get_json()['active'] is False

    def test_lottery_round_not_returned_by_ichiban_active(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_lottery_round(client, p_token)
        assert get_active(client, p_token).get_json()['active'] is False

    def test_ichiban_draw_needs_ichiban_round(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_tickets(client, p_token)
        create_lottery_round(client, p_token)
        assert draw(client, c_token).status_code == 400

    def test_lottery_draw_needs_lottery_round(self, client):
        _, c_token = setup_round(client)
        r = client.post('/api/lottery/draw', json={'tickets': 1}, headers=auth(c_token))
        assert r.status_code == 400

    def test_histories_do_not_mix(self, client):
        p_token, c_token = setup_round(client)
        draw(client, c_token, 2)
        create_lottery_round(client, p_token)
        client.post('/api/lottery/draw', json={'tickets': 3}, headers=auth(c_token))

        ichiban = get_history(client, c_token).get_json()['results']
        lottery = client.get('/api/lottery/history?child_id=kid1',
                             headers=auth(c_token)).get_json()['results']
        assert len(ichiban) == 2
        assert len(lottery) == 3
        assert all(r['grade'] is not None for r in ichiban)

    def test_round_lists_do_not_mix(self, client):
        p_token, _ = setup_round(client)
        create_lottery_round(client, p_token)
        ichiban = client.get('/api/ichiban/rounds?child_id=kid1',
                             headers=auth(p_token)).get_json()['rounds']
        lottery = client.get('/api/lottery/rounds?child_id=kid1',
                             headers=auth(p_token)).get_json()['rounds']
        assert len(ichiban) == 1 and ichiban[0]['mode'] == 'ichiban'
        assert len(lottery) == 1 and lottery[0]['mode'] == 'random'

    def test_lottery_cannot_finish_ichiban_round(self, client):
        p_token, _ = setup_round(client)
        round_id = get_active(client, p_token).get_json()['round']['id']
        r = client.post(f'/api/lottery/rounds/{round_id}/finish', headers=auth(p_token))
        assert r.status_code == 404

    def test_ichiban_cannot_finish_lottery_round(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        round_id = create_lottery_round(client, p_token).get_json()['id']
        r = client.post(f'/api/ichiban/rounds/{round_id}/finish', headers=auth(p_token))
        assert r.status_code == 404

    def test_both_features_draw_from_the_same_ticket_pool(self, client):
        p_token, c_token = setup_round(client, tickets=10)
        create_lottery_round(client, p_token)
        assert draw(client, c_token, 4).get_json()['remaining_tickets'] == 6
        # A classic-lottery draw may stop early on a jackpot, so spend against what it reports.
        lottery = client.post('/api/lottery/draw', json={'tickets': 3},
                              headers=auth(c_token)).get_json()
        assert lottery['remaining_tickets'] == 6 - lottery['tickets_used']
