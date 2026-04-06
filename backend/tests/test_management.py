from helpers import setup_parent, setup_child, create_child, login_child, auth


class TestCreateChild:
    def test_custom_id(self, client):
        _, p_token = setup_parent(client)
        r = create_child(client, p_token, child_id='kid1')
        assert r.status_code == 201
        assert r.get_json()['child_id'] == 'kid1'

    def test_auto_generated_id(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/management/create-child', json={
            'name': 'Auto Kid', 'password': 'kidpass'
        }, headers=auth(p_token))
        assert r.status_code == 201
        assert r.get_json()['child_id'] is not None

    def test_duplicate_id(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token, child_id='kid1')
        r = create_child(client, p_token, child_id='kid1')
        assert r.status_code == 400
        assert 'already taken' in r.get_json()['error']

    def test_invalid_id_format(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/management/create-child', json={
            'id': 'invalid id!', 'name': 'Kid', 'password': 'kidpass'
        }, headers=auth(p_token))
        assert r.status_code == 400

    def test_missing_name(self, client):
        _, p_token = setup_parent(client)
        r = client.post('/api/management/create-child', json={
            'password': 'kidpass'
        }, headers=auth(p_token))
        assert r.status_code == 400

    def test_child_cannot_create(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.post('/api/management/create-child', json={
            'name': 'Another', 'password': 'pass'
        }, headers=auth(c_token))
        assert r.status_code == 403


class TestDeleteChild:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token, child_id='kid1')
        r = client.delete('/api/management/delete-child/kid1', headers=auth(p_token))
        assert r.status_code == 200

    def test_wrong_parent(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token, child_id='kid1')
        _, p2_token = setup_parent(client, username='parent2', email='p2@test.com')
        r = client.delete('/api/management/delete-child/kid1', headers=auth(p2_token))
        assert r.status_code == 404

    def test_nonexistent_child(self, client):
        _, p_token = setup_parent(client)
        r = client.delete('/api/management/delete-child/nobody', headers=auth(p_token))
        assert r.status_code == 404


class TestUpdateChildPassword:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token, child_id='kid1', password='oldpass')
        r = client.post('/api/management/update-child-password/kid1', json={
            'new_password': 'newpass'
        }, headers=auth(p_token))
        assert r.status_code == 200
        # verify new password works
        r2 = client.post('/api/auth/child/login', json={
            'child_id': 'kid1', 'password': 'newpass'
        })
        assert r2.status_code == 200

    def test_missing_password(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token)
        r = client.post('/api/management/update-child-password/kid1', json={},
                        headers=auth(p_token))
        assert r.status_code == 400


class TestUpdateChildName:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token)
        r = client.post('/api/management/update-child-name/kid1', json={
            'new_name': 'New Name'
        }, headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['child_name'] == 'New Name'

    def test_missing_name(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token)
        r = client.post('/api/management/update-child-name/kid1', json={},
                        headers=auth(p_token))
        assert r.status_code == 400


class TestUpdateChildAge:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token)
        r = client.post('/api/management/update-child-age/kid1', json={
            'age': 10
        }, headers=auth(p_token))
        assert r.status_code == 200
        assert r.get_json()['age'] == 10

    def test_missing_age(self, client):
        _, p_token = setup_parent(client)
        create_child(client, p_token)
        r = client.post('/api/management/update-child-age/kid1', json={},
                        headers=auth(p_token))
        assert r.status_code == 400
