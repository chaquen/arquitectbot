def test_get_components_empty(client):
    response = client.get('/components')
    assert response.status_code == 200
    assert response.json == []

def test_create_component(client):
    data = {
        'name': 'Test Component',
        'type': 'Service',
        'description': 'Test Description'
    }
    response = client.post('/components', json=data)
    assert response.status_code == 201
    assert response.json['name'] == data['name']
    assert response.json['type'] == data['type']
    assert response.json['description'] == data['description']

def test_get_component(client):
    # First create a component
    data = {
        'name': 'Test Component',
        'type': 'Service',
        'description': 'Test Description'
    }
    create_response = client.post('/components', json=data)
    component_id = create_response.json['id']

    # Then get it
    response = client.get(f'/components/{component_id}')
    assert response.status_code == 200
    assert response.json['name'] == data['name']
    assert response.json['type'] == data['type']
    assert response.json['description'] == data['description']

def test_update_component(client):
    # First create a component
    data = {
        'name': 'Test Component',
        'type': 'Service',
        'description': 'Test Description'
    }
    create_response = client.post('/components', json=data)
    component_id = create_response.json['id']

    # Then update it
    update_data = {
        'name': 'Updated Component',
        'type': 'Microservice',
        'description': 'Updated Description'
    }
    response = client.put(f'/components/{component_id}', json=update_data)
    assert response.status_code == 200
    assert response.json['name'] == update_data['name']
    assert response.json['type'] == update_data['type']
    assert response.json['description'] == update_data['description']

def test_delete_component(client):
    # First create a component
    data = {
        'name': 'Test Component',
        'type': 'Service',
        'description': 'Test Description'
    }
    create_response = client.post('/components', json=data)
    component_id = create_response.json['id']

    # Then delete it
    response = client.delete(f'/components/{component_id}')
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f'/components/{component_id}')
    assert get_response.status_code == 404
