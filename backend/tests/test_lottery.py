from helpers import setup_parent, setup_child, auth


def add_record(client, child_token, minutes=30, date='2026-01-15'):
    return client.post('/api/practice/record', json={
        'practice_minutes': minutes, 'date': date
    }, headers=auth(child_token))


def approve_record(client, p_token, record_id):
    return client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p_token))


def get_record_id(client, p_token, child_id='kid1'):
    records = client.get(f'/api/practice/records/{child_id}', headers=auth(p_token)).get_json()
    return records['records'][0]['id']


def get_balance(client, token, child_id='kid1'):
    return client.get(f'/api/awards/balance/{child_id}', headers=auth(token)).get_json()


class TestApproveGivesLotteryTickets:
    """每 15 分鐘練琴獲得 1 張抽獎卷"""

    def _setup_and_approve(self, client, minutes):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token, minutes=minutes)
        record_id = get_record_id(client, p_token)
        r = approve_record(client, p_token, record_id)
        return p_token, c_token, r

    def test_15min_gives_1_ticket(self, client):
        _, _, r = self._setup_and_approve(client, minutes=15)
        assert r.status_code == 200
        data = r.get_json()
        assert data['lottery_tickets_earned'] == 1
        assert data['child_lottery_tickets'] == 1

    def test_30min_gives_2_tickets(self, client):
        _, _, r = self._setup_and_approve(client, minutes=30)
        data = r.get_json()
        assert data['lottery_tickets_earned'] == 2
        assert data['child_lottery_tickets'] == 2

    def test_45min_gives_3_tickets(self, client):
        _, _, r = self._setup_and_approve(client, minutes=45)
        data = r.get_json()
        assert data['lottery_tickets_earned'] == 3
        assert data['child_lottery_tickets'] == 3

    def test_60min_gives_4_tickets(self, client):
        _, _, r = self._setup_and_approve(client, minutes=60)
        data = r.get_json()
        assert data['lottery_tickets_earned'] == 4
        assert data['child_lottery_tickets'] == 4

    def test_tickets_accumulate_across_approvals(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)

        add_record(client, c_token, minutes=30, date='2026-01-15')
        record_id = get_record_id(client, p_token)
        approve_record(client, p_token, record_id)

        add_record(client, c_token, minutes=45, date='2026-01-16')
        record_id = get_record_id(client, p_token)
        approve_record(client, p_token, record_id)

        balance = get_balance(client, p_token)
        assert balance['lottery_tickets'] == 5  # 2 + 3

    def test_balance_api_reflects_lottery_tickets(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token, minutes=30)
        record_id = get_record_id(client, p_token)
        approve_record(client, p_token, record_id)

        balance = get_balance(client, p_token)
        assert balance['lottery_tickets'] == 2

    def test_new_child_starts_with_zero_tickets(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        balance = get_balance(client, p_token)
        assert balance['lottery_tickets'] == 0

    def test_reject_does_not_give_tickets(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token, minutes=30)
        record_id = get_record_id(client, p_token)
        client.post(f'/api/practice/record/{record_id}/reject', headers=auth(p_token))

        balance = get_balance(client, p_token)
        assert balance['lottery_tickets'] == 0


class TestGiveLotteryTickets:
    """家長手動給予抽獎卷"""

    def test_success(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': 3
        }, headers=auth(p_token))
        assert r.status_code == 201
        data = r.get_json()
        assert data['quantity_given'] == 3
        assert data['lottery_tickets'] == 3

    def test_tickets_stack_with_practice_tickets(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)

        # Approve 30 min → 2 tickets
        add_record(client, c_token, minutes=30)
        record_id = get_record_id(client, p_token)
        approve_record(client, p_token, record_id)

        # Parent manually gives 5 more
        client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': 5
        }, headers=auth(p_token))

        balance = get_balance(client, p_token)
        assert balance['lottery_tickets'] == 7  # 2 + 5

    def test_child_cannot_give_lottery(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': 1
        }, headers=auth(c_token))
        assert r.status_code == 403

    def test_wrong_child_id(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'nobody', 'quantity': 1
        }, headers=auth(p_token))
        assert r.status_code == 404

    def test_missing_child_id(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/awards/give-lottery', json={
            'quantity': 1
        }, headers=auth(p_token))
        assert r.status_code == 400

    def test_missing_quantity(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1'
        }, headers=auth(p_token))
        assert r.status_code == 400

    def test_zero_quantity_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': 0
        }, headers=auth(p_token))
        assert r.status_code == 400

    def test_negative_quantity_rejected(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': -2
        }, headers=auth(p_token))
        assert r.status_code == 400

    def test_cannot_give_to_other_parents_child(self, client):
        _, p1_token = setup_parent(client, username='parent1', email='p1@test.com')
        _, p2_token = setup_parent(client, username='parent2', email='p2@test.com')
        setup_child(client, p1_token, child_id='kid1')
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': 1
        }, headers=auth(p2_token))
        assert r.status_code == 404

    def test_multiple_gives_accumulate(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': 2
        }, headers=auth(p_token))
        r = client.post('/api/awards/give-lottery', json={
            'child_id': 'kid1', 'quantity': 3
        }, headers=auth(p_token))
        assert r.get_json()['lottery_tickets'] == 5
