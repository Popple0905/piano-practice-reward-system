from helpers import setup_parent, setup_child, auth


def create_item(client, p_token, child_id='kid1', content='Movie night', cost=50,
                quantity=None, expires_at=None):
    body = {'child_id': child_id, 'content': content, 'points_cost': cost}
    if quantity is not None:
        body['quantity'] = quantity
    if expires_at is not None:
        body['expires_at'] = expires_at
    return client.post('/api/special-redemptions/', json=body, headers=auth(p_token))


def give_balance(client, p_token, amount=100):
    client.post('/api/awards/give', json={
        'child_id': 'kid1', 'game_minutes': amount
    }, headers=auth(p_token))


class TestCreateSpecialRedemption:
    def test_success_unlimited(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_item(client, p_token)
        assert r.status_code == 201
        assert r.get_json()['quantity'] is None

    def test_success_with_quantity(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_item(client, p_token, quantity=3)
        assert r.status_code == 201
        assert r.get_json()['quantity'] == 3

    def test_invalid_points_cost(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_item(client, p_token, cost=0)
        assert r.status_code == 400

    def test_invalid_quantity_zero(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = create_item(client, p_token, quantity=0)
        assert r.status_code == 400

    def test_wrong_child(self, client):
        _, p_token = setup_parent(client)
        r = create_item(client, p_token, child_id='nobody')
        assert r.status_code == 404

    def test_child_cannot_create(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.post('/api/special-redemptions/', json={
            'child_id': 'kid1', 'content': 'Test', 'points_cost': 10
        }, headers=auth(c_token))
        assert r.status_code == 403

    def test_missing_fields(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/special-redemptions/', json={
            'child_id': 'kid1'
        }, headers=auth(p_token))
        assert r.status_code == 400


class TestListRedemptions:
    def test_parent_list(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        create_item(client, p_token)
        r = client.get('/api/special-redemptions/parent', headers=auth(p_token))
        assert r.status_code == 200
        assert len(r.get_json()['items']) == 1

    def test_child_list_only_active(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        create_item(client, p_token, content='Active')
        # expired item
        create_item(client, p_token, content='Expired',
                    expires_at='2020-01-01T00:00:00Z')
        # out of stock item
        create_item(client, p_token, content='OOS', quantity=0)
        r = client.get('/api/special-redemptions/child/kid1', headers=auth(c_token))
        assert r.status_code == 200
        items = r.get_json()['items']
        # only the active one should appear
        assert len(items) == 1
        assert items[0]['content'] == 'Active'


class TestDeleteRedemption:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        item_id = create_item(client, p_token).get_json()['id']
        r = client.delete(f'/api/special-redemptions/{item_id}', headers=auth(p_token))
        assert r.status_code == 200

    def test_wrong_parent(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        item_id = create_item(client, p_token).get_json()['id']
        _, p2_token = setup_parent(client, username='parent2', email='p2@test.com')
        r = client.delete(f'/api/special-redemptions/{item_id}', headers=auth(p2_token))
        assert r.status_code == 404


class TestRedeemItem:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_balance(client, p_token, 100)
        item_id = create_item(client, p_token, cost=50).get_json()['id']
        r = client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(c_token))
        assert r.status_code == 200
        assert r.get_json()['remaining_balance'] == 50

    def test_quantity_decremented(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_balance(client, p_token, 100)
        item_id = create_item(client, p_token, cost=10, quantity=2).get_json()['id']
        client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(c_token))
        # check quantity via parent list
        items = client.get('/api/special-redemptions/parent', headers=auth(p_token)).get_json()['items']
        assert items[0]['quantity'] == 1

    def test_insufficient_balance(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        item_id = create_item(client, p_token, cost=50).get_json()['id']
        r = client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(c_token))
        assert r.status_code == 400
        assert 'Insufficient' in r.get_json()['error']

    def test_expired_item(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_balance(client, p_token, 100)
        item_id = create_item(client, p_token, cost=10,
                              expires_at='2020-01-01T00:00:00Z').get_json()['id']
        r = client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(c_token))
        assert r.status_code == 400
        assert 'expired' in r.get_json()['error']

    def test_out_of_stock(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_balance(client, p_token, 100)
        item_id = create_item(client, p_token, cost=10, quantity=1).get_json()['id']
        # redeem once to exhaust stock
        client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(c_token))
        r = client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(c_token))
        assert r.status_code == 400
        assert 'out of stock' in r.get_json()['error']

    def test_parent_cannot_redeem(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        item_id = create_item(client, p_token, cost=10).get_json()['id']
        r = client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(p_token))
        assert r.status_code == 403


class TestRedemptionRecords:
    def test_records_returned(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        give_balance(client, p_token, 100)
        item_id = create_item(client, p_token, cost=30, content='Movie').get_json()['id']
        client.post(f'/api/special-redemptions/{item_id}/redeem', headers=auth(c_token))
        r = client.get('/api/special-redemptions/records/kid1', headers=auth(p_token))
        assert r.status_code == 200
        records = r.get_json()['records']
        assert len(records) == 1
        assert records[0]['content'] == 'Movie'
        assert records[0]['points_spent'] == 30
