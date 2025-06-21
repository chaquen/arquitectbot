from flask import Blueprint, request, jsonify
from app.application.component_service import ComponentService
from flasgger import swag_from

bp = Blueprint('component_api', __name__)
service = ComponentService()

@bp.route('/components', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List of components',
            'examples': {
                'application/json': [
                    {'label': 'Component A', 'component_type': 'Service', 'type': 'API', 'location': 'Cloud', 'technology': 'Python', 'host': 'host1', 'description': '...', 'interface': 'REST'}
                ]
            }
        }
    }
})
def get_components():
    """
    Retrieve all components.
    Returns:
        JSON list of all components.
    """
    components = service.get_all_components()
    return jsonify([c.to_dict() for c in components]), 200

@bp.route('/components/<component_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'component_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID of the component to retrieve'
        }
    ],
    'responses': {200: {'description': 'Component found'}, 404: {'description': 'Not found'}}})
def get_component(component_id):
    """
    Retrieve a component by its ID.
    Args:
        component_id (str): The component's unique identifier.
    Returns:
        JSON of the component or error message.
    """
    component = service.get_component(component_id)
    if component:
        return jsonify(component.to_dict()), 200
    return jsonify({'error': 'Not found'}), 404

@bp.route('/components', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'label': {'type': 'string'},
                    'component_type': {'type': 'string'},
                    'type': {'type': 'string'},
                    'location': {'type': 'string'},
                    'technology': {'type': 'string'},
                    'host': {'type': 'string'},
                    'description': {'type': 'string'},
                    'interface': {'type': 'string'}
                },
                'required': ['label', 'component_type', 'type', 'location', 'technology', 'host', 'description', 'interface']
            }
        }
    ],
    'responses': {201: {'description': 'Created'}, 400: {'description': 'Validation error'}}
})
def create_component():
    """
    Create a new component from JSON body.
    Returns:
        JSON of the created component or error message.
    """
    data = request.get_json()
    try:
        component = service.create_component(data)
        return jsonify(component.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/components/<component_id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'label': {'type': 'string'},
                    'component_type': {'type': 'string'},
                    'type': {'type': 'string'},
                    'location': {'type': 'string'},
                    'technology': {'type': 'string'},
                    'host': {'type': 'string'},
                    'description': {'type': 'string'},
                    'interface': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {200: {'description': 'Updated'}, 404: {'description': 'Not found'}}
})
def update_component(component_id):
    """
    Update an existing component by its ID.
    Args:
        component_id (str): The component's unique identifier.
    Returns:
        JSON of the updated component or error message.
    """
    data = request.get_json()
    component = service.update_component(component_id, data)
    if component:
        return jsonify(component.to_dict()), 200
    return jsonify({'error': 'Not found'}), 404

@bp.route('/components/<component_id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'component_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID of the component to delete'
        }
    ],
    'responses': {204: {'description': 'Deleted'}, 404: {'description': 'Not found'}}
})
def delete_component(component_id):
    """
    Delete a component by its ID.
    Args:
        component_id (str): The component's unique identifier.
    Returns:
        Empty response or error message.
    """
    if service.delete_component(component_id):
        return '', 204
    return jsonify({'error': 'Not found'}), 404

@bp.route('/components/<id_from>/connect/<id_to>', methods=['POST'])
@swag_from({
    'parameters': [
        {'name': 'id_from', 'in': 'path', 'type': 'string', 'required': True},
        {'name': 'id_to', 'in': 'path', 'type': 'string', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'connection_type': {'type': 'string'},
                    'protocol': {'type': 'string'},
                    'port': {'type': 'integer'},
                    'usage': {'type': 'string'},
                    'authenticated': {'type': 'boolean'},
                    'authentication': {'type': 'string'},
                    'encryption': {'type': 'string'}
                },
                'required': ['connection_type', 'protocol', 'port']
            }
        }
    ],
    'responses': {201: {'description': 'Connection created'}, 400: {'description': 'Error'}}
})
def connect_components(id_from, id_to):
    """
    Create a CONNECTS_TO relationship between two components.
    Args:
        id_from (str): ID of the source component.
        id_to (str): ID of the target component.
    Returns:
        JSON message indicating success or error.
    """
    props = request.get_json()
    ok = service.connect_components(id_from, id_to, props)
    if ok:
        return jsonify({'message': 'Connection created'}), 201
    return jsonify({'error': 'Could not create connection'}), 400
