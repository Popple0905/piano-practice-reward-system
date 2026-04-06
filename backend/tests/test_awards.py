from helpers import setup_parent, setup_child, auth


class TestGiveAward:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/awards/give', json={
            'child_id': 'kid1', 'game_minutes': 60, 'reason': 'Good job'
        }, headers=auth(p_token))
        assert r.status_code == 201
        assert r.get_json()['new_balance'] == 60

    def test_child_cannot_give(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.post('/api/awards/give', json={
            'child_id': 'kid1', 'game_minutes': 60
        }, headers=auth(c_token))
        assert r.status_code == 403

    def test_wrong_child(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/awards/give', json={
            'child_id': 'nobody', 'game_minutes': 60
        }, headers=auth(p_token))
        assert r.status_code == 404

    def test_missing_fields(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/awards/give', json={
            'child_id': 'kid1'
        }, headers=auth(p_token))
        assert r.status_code == 400


class TestRequestGameTime:
    def _give_balance(self, client, p_token, amount=60):
        client.post('/api/awards/give', json={
            'child_id': 'kid1', 'game_minutes': amount
        }, headers=auth(p_token))

    def test_success(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        self._give_balance(client, p_token, 60)
        r = client.post('/api/awards/request', json={'game_minutes': 30}, headers=auth(c_token))
        assert r.status_code == 200
        assert r.get_json()['remaining_balance'] == 30

    def test_not_multiple_of_15(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        self._give_balance(client, p_token, 60)
        r = client.post('/api/awards/request', json={'game_minutes': 20}, headers=auth(c_token))
        assert r.status_code == 400
        assert '15' in r.get_json()['error']

    def test_insufficient_balance(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        self._give_balance(client, p_token, 15)
        r = client.post('/api/awards/request', json={'game_minutes': 30}, headers=auth(c_token))
        assert r.status_code == 400
        assert 'Insufficient' in r.get_json()['error']

    def test_parent_cannot_request(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/awards/request', json={'game_minutes': 15}, headers=auth(p_token))
        assert r.status_code == 403


class TestGetBalance:
    def test_parent_can_view(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.get('/api/awards/balance/kid1', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['game_balance'] == 0

    def test_child_can_view_self(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.get('/api/awards/balance/kid1', headers=auth(c_token))
        assert r.status_code == 200

    def test_child_cannot_view_other(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token, child_id='kid1')
        setup_child(client, p_token, child_id='kid2', name='Kid Two')
        r = client.get('/api/awards/balance/kid2', headers=auth(c_token))
        assert r.status_code == 403


class TestAwardHistory:
    def test_history_returned(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        client.post('/api/awards/give', json={
            'child_id': 'kid1', 'game_minutes': 30
        }, headers=auth(p_token))
        r = client.get('/api/awards/history/kid1', headers=auth(p_token))
        assert r.status_code == 200
        data = r.get_json()
        assert data['total_awards'] == 1
        assert data['total_minutes_given'] == 30


class TestRatio:
    def test_get_ratio(self, client):
        _, p_token = setup_parent(client)
        r = client.get('/api/awards/ratio', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['practice_to_game_ratio'] == 1.0

    def test_set_ratio(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/awards/ratio', json={'ratio': 2.0}, headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['new_ratio'] == 2.0

    def test_set_invalid_ratio(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/awards/ratio', json={'ratio': -1}, headers=auth(p_token))
        assert r.status_code == 400

    def test_set_ratio_affects_approval_reward(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        client.post('/api/awards/ratio', json={'ratio': 2.0}, headers=auth(p_token))
        client.post('/api/practice/record', json={
            'practice_minutes': 30, 'date': '2026-01-15'
        }, headers=auth(c_token))
        records = client.get('/api/practice/records/kid1', headers=auth(p_token)).get_json()
        record_id = records['records'][0]['id']
        r = client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p_token))
        assert r.get_json()['game_minutes_earned'] == 60  # 30 min * ratio 2.0

    def test_child_can_get_ratio(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.get('/api/awards/ratio', headers=auth(c_token))
        assert r.status_code == 200
