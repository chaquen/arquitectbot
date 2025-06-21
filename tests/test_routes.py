def test_get_components_empty(client):
    response = client.get('/components')
    assert response.status_code == 200
    assert response.json == []

def test_create_component(client):
    data = {
        'label': 'Test Component',
        'component_type': 'Service',
        'category': 'API',
        'location': 'Cloud',
        'technology': 'Python',
        'host': 'host1',
        'description': 'Test Description',
        'interface': 'REST'
    }
    response = client.post('/components', json=data)
    assert response.status_code == 201
    for key in data:
        assert response.json[key] == data[key]

def test_get_component(client):
    # First create a component
    data = {
        'label': 'Test Component',
        'component_type': 'Service',
        'category': 'API',
        'location': 'Cloud',
        'technology': 'Python',
        'host': 'host1',
        'description': 'Test Description',
        'interface': 'REST'
    }
    create_response = client.post('/components', json=data)
    component_id = create_response.json['id']

    # Then get it
    response = client.get(f'/components/{component_id}')
    assert response.status_code == 200
    for key in data:
        assert response.json[key] == data[key]

def test_update_component(client):
    # First create a component
    data = {
        'label': 'Test Component',
        'component_type': 'Service',
        'category': 'API',
        'location': 'Cloud',
        'technology': 'Python',
        'host': 'host1',
        'description': 'Test Description',
        'interface': 'REST'
    }
    create_response = client.post('/components', json=data)
    component_id = create_response.json['id']

    # Then update it
    update_data = {
        'label': 'Updated Component',
        'component_type': 'Microservice',
        'category': 'DB',
        'location': 'OnPrem',
        'technology': 'Go',
        'host': 'host2',
        'description': 'Updated Description',
        'interface': 'gRPC'
    }
    response = client.put(f'/components/{component_id}', json=update_data)
    assert response.status_code == 200
    for key in update_data:
        assert response.json[key] == update_data[key]

def test_delete_component(client):
    # First create a component
    data = {
        'label': 'Test Component',
        'component_type': 'Service',
        'category': 'API',
        'location': 'Cloud',
        'technology': 'Python',
        'host': 'host1',
        'description': 'Test Description',
        'interface': 'REST'
    }
    create_response = client.post('/components', json=data)
    component_id = create_response.json['id']

    # Then delete it
    response = client.delete(f'/components/{component_id}')
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f'/components/{component_id}')
    assert get_response.status_code == 404
