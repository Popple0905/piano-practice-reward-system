def auth(token):
    return {'Authorization': f'Bearer {token}'}


def register_parent(client, username='parent1', password='pass1234', email='p@test.com'):
    return client.post('/api/auth/parent/register', json={
        'username': username, 'password': password, 'email': email
    })


def login_parent(client, username='parent1', password='pass1234'):
    res = client.post('/api/auth/parent/login', json={
        'username': username, 'password': password
    })
    return res.get_json()['access_token']


def setup_parent(client, username='parent1', password='pass1234', email='p@test.com'):
    r = register_parent(client, username, password, email)
    parent_id = r.get_json()['parent_id']
    token = login_parent(client, username, password)
    return parent_id, token


def create_child(client, token, child_id='kid1', name='Kid One', password='kidpass'):
    return client.post('/api/management/create-child', json={
        'id': child_id, 'name': name, 'password': password
    }, headers=auth(token))


def login_child(client, child_id='kid1', password='kidpass'):
    res = client.post('/api/auth/child/login', json={
        'child_id': child_id, 'password': password
    })
    return res.get_json()['access_token']


def setup_child(client, parent_token, child_id='kid1', name='Kid One', password='kidpass'):
    create_child(client, parent_token, child_id, name, password)
    return login_child(client, child_id, password)
