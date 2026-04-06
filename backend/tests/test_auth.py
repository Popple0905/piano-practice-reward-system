from helpers import register_parent, login_parent, setup_parent, setup_child, auth


class TestParentRegister:
    def test_success(self, client):
        r = register_parent(client)
        assert r.status_code == 201
        assert 'parent_id' in r.get_json()

    def test_duplicate_username(self, client):
        register_parent(client)
        r = register_parent(client)
        assert r.status_code == 400
        assert 'already exists' in r.get_json()['error']

    def test_missing_fields(self, client):
        r = client.post('/api/auth/parent/register', json={'username': 'x'})
        assert r.status_code == 400


class TestParentLogin:
    def test_success(self, client):
        register_parent(client)
        r = client.post('/api/auth/parent/login', json={
            'username': 'parent1', 'password': 'pass1234'
        })
        assert r.status_code == 200
        assert 'access_token' in r.get_json()

    def test_wrong_password(self, client):
        register_parent(client)
        r = client.post('/api/auth/parent/login', json={
            'username': 'parent1', 'password': 'wrong'
        })
        assert r.status_code == 401

    def test_nonexistent_user(self, client):
        r = client.post('/api/auth/parent/login', json={
            'username': 'nobody', 'password': 'pass1234'
        })
        assert r.status_code == 401

    def test_missing_fields(self, client):
        r = client.post('/api/auth/parent/login', json={'username': 'parent1'})
        assert r.status_code == 400


class TestChildLogin:
    def test_success(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/auth/child/login', json={
            'child_id': 'kid1', 'password': 'kidpass'
        })
        assert r.status_code == 200
        assert 'access_token' in r.get_json()

    def test_wrong_password(self, client):
        _, p_token = setup_parent(client)
        setup_child(client, p_token)
        r = client.post('/api/auth/child/login', json={
            'child_id': 'kid1', 'password': 'wrong'
        })
        assert r.status_code == 401

    def test_missing_fields(self, client):
        r = client.post('/api/auth/child/login', json={'child_id': 'kid1'})
        assert r.status_code == 400


class TestChangePassword:
    def test_success(self, client):
        register_parent(client)
        token = login_parent(client)
        r = client.post('/api/auth/parent/change-password', json={
            'current_password': 'pass1234', 'new_password': 'newpass99'
        }, headers=auth(token))
        assert r.status_code == 200
        # verify new password works
        r2 = client.post('/api/auth/parent/login', json={
            'username': 'parent1', 'password': 'newpass99'
        })
        assert r2.status_code == 200

    def test_wrong_current_password(self, client):
        register_parent(client)
        token = login_parent(client)
        r = client.post('/api/auth/parent/change-password', json={
            'current_password': 'wrong', 'new_password': 'newpass99'
        }, headers=auth(token))
        assert r.status_code == 401

    def test_short_new_password(self, client):
        register_parent(client)
        token = login_parent(client)
        r = client.post('/api/auth/parent/change-password', json={
            'current_password': 'pass1234', 'new_password': 'ab'
        }, headers=auth(token))
        assert r.status_code == 400

    def test_child_cannot_call(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.post('/api/auth/parent/change-password', json={
            'current_password': 'kidpass', 'new_password': 'newkidpass'
        }, headers=auth(c_token))
        assert r.status_code == 403


class TestGetParentInfo:
    def test_success(self, client):
        register_parent(client)
        token = login_parent(client)
        r = client.get('/api/auth/parent/me', headers=auth(token))
        assert r.status_code == 200
        data = r.get_json()
        assert data['username'] == 'parent1'
        assert 'children' in data

    def test_child_cannot_call(self, client):
        _, p_token = setup_parent(client)
        c_token = setup_child(client, p_token)
        r = client.get('/api/auth/parent/me', headers=auth(c_token))
        assert r.status_code == 403
