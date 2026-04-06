from helpers import setup_parent, setup_child, auth


def add_record(client, child_token, minutes=30, date='2026-01-15'):
    return client.post('/api/practice/record', json={
        'practice_minutes': minutes, 'date': date
    }, headers=auth(child_token))


class TestAddPracticeRecord:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = add_record(client, c_token)
        assert r.status_code == 201
        assert r.get_json()['status'] == 'pending'

    def test_invalid_duration_not_multiple_of_15(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = add_record(client, c_token, minutes=20)
        assert r.status_code == 400
        assert '15' in r.get_json()['error']

    def test_duplicate_date_updates_existing(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token, minutes=30, date='2026-01-15')
        r = add_record(client, c_token, minutes=45, date='2026-01-15')
        assert r.status_code == 201
        assert r.get_json()['practice_minutes'] == 45

    def test_parent_cannot_add(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/practice/record', json={
            'practice_minutes': 30
        }, headers=auth(p_token))
        assert r.status_code == 403

    def test_missing_minutes(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.post('/api/practice/record', json={}, headers=auth(c_token))
        assert r.status_code == 400


class TestApproveRecord:
    def _setup(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token)
        # get record id
        records = client.get('/api/practice/records/kid1', headers=auth(p_token)).get_json()
        record_id = records['records'][0]['id']
        return p_token, c_token, record_id

    def test_approve_success(self, client):
        p_token, _, record_id = self._setup(client)
        r = client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p_token))
        assert r.status_code == 200
        data = r.get_json()
        assert data['game_minutes_earned'] == 30  # ratio 1.0 default
        assert data['child_new_balance'] == 30

    def test_approve_wrong_parent(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token)
        # second parent
        _, p2_token = setup_parent(client, username='parent2', email='p2@test.com')
        records = client.get('/api/practice/records/kid1', headers=auth(p_token)).get_json()
        record_id = records['records'][0]['id']
        r = client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p2_token))
        assert r.status_code == 403

    def test_approve_already_approved(self, client):
        p_token, _, record_id = self._setup(client)
        client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p_token))
        r = client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p_token))
        assert r.status_code == 400

    def test_child_cannot_approve(self, client):
        _, c_token, record_id = self._setup(client)
        r = client.post(f'/api/practice/record/{record_id}/approve', headers=auth(c_token))
        assert r.status_code == 403


class TestRejectRecord:
    def test_reject_success(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token)
        records = client.get('/api/practice/records/kid1', headers=auth(p_token)).get_json()
        record_id = records['records'][0]['id']
        r = client.post(f'/api/practice/record/{record_id}/reject', headers=auth(p_token))
        assert r.status_code == 200

    def test_reject_already_approved(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token)
        records = client.get('/api/practice/records/kid1', headers=auth(p_token)).get_json()
        record_id = records['records'][0]['id']
        client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p_token))
        r = client.post(f'/api/practice/record/{record_id}/reject', headers=auth(p_token))
        assert r.status_code == 400


class TestGetRecords:
    def test_parent_can_view_own_child(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token, date='2026-01-15')
        r = client.get('/api/practice/records/kid1', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['total_records'] == 1

    def test_child_can_view_self(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token)
        r = client.get('/api/practice/records/kid1', headers=auth(c_token))
        assert r.status_code == 200

    def test_child_cannot_view_other(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token, child_id='kid1')
        setup_child(client, p_token, child_id='kid2', name='Kid Two')
        r = client.get('/api/practice/records/kid2', headers=auth(c_token))
        assert r.status_code == 403

    def test_status_filter(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token)
        r = client.get('/api/practice/records/kid1?status=approved', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['total_records'] == 0


class TestStatistics:
    def test_no_records(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.get('/api/practice/statistics/kid1', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['total_approved_minutes'] == 0

    def test_approved_records_counted(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        add_record(client, c_token, minutes=30, date='2026-01-15')
        records = client.get('/api/practice/records/kid1', headers=auth(p_token)).get_json()
        record_id = records['records'][0]['id']
        client.post(f'/api/practice/record/{record_id}/approve', headers=auth(p_token))
        r = client.get('/api/practice/statistics/kid1', headers=auth(p_token))
        assert r.get_json()['total_approved_minutes'] == 30
        assert r.get_json()['days_practiced'] == 1


class TestGetParentChildren:
    def test_returns_children_list(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token, child_id='kid1')
        setup_child(client, p_token, child_id='kid2', name='Kid Two')
        r = client.get('/api/practice/parent/children', headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['children_count'] == 2
