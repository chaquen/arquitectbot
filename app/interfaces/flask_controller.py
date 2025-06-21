from flask import Blueprint, request, jsonify, current_app
from app.application.component_service import ComponentService
from flasgger import swag_from

bp = Blueprint('component_api', __name__)
# Use a function to create service on demand instead of at module load time
def get_service():
    return ComponentService()

@bp.route('/components', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List of components',
            'examples': {
                'application/json': [
                    {'label': 'Component A', 'component_type': 'Service', 'category': 'API', 'location': 'Cloud', 'technology': 'Python', 'host': 'host1', 'description': '...', 'interface': 'REST'}
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
    components = get_service().get_all_components()
    return jsonify([c.to_dict() for c in components]), 200

@bp.route('/components/<component_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'component_id',
            'in': 'path',
            'category': 'string',
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
    component = get_service().get_component(component_id)
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
                    'category': {'type': 'string'},
                    'location': {'type': 'string'},
                    'technology': {'type': 'string'},
                    'host': {'type': 'string'},
                    'description': {'type': 'string'},
                    'interface': {'type': 'string'}
                },
                'required': ['label', 'component_type', 'category', 'location', 'technology', 'host', 'description', 'interface']
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
        component = get_service().create_component(data)
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
                    'category': {'type': 'string'},
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
    component = get_service().update_component(component_id, data)
    if component:
        return jsonify(component.to_dict()), 200
    return jsonify({'error': 'Not found'}), 404

@bp.route('/components/<component_id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'component_id',
            'in': 'path',
            'category': 'string',
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
    if get_service().delete_component(component_id):
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
    ok = get_service().connect_components(id_from, id_to, props)
    if ok:
        return jsonify({'message': 'Connection created'}), 201
    return jsonify({'error': 'Could not create connection'}), 400

@bp.route('/import-nodes-components', methods=['POST'])
@swag_from({
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'CSV file with columns: id, label, component_type, category, location, technology, host, description, interface'
        }
    ],
    'responses': {
        200: {
            'description': 'List of imported components',
            'schema': {
                'type': 'array',
                'items': {'type': 'object'}
            }
        },
        201: {
            'description': 'Nodes created in Neo4j',
            'schema': {
                'type': 'object'
            }
        },
        400: {'description': 'Validation or file error'}
    }
})
def import_nodes_components():
    """
    Import component nodes from a CSV file. The CSV must have columns:
    id, label, component_type, category, location, technology, host, description, interface
    Always creates nodes in Neo4j.
    Returns:
        JSON result of created/skipped components or error message.
    """
    from app.services import import_nodes_components_from_csv, import_and_create_nodes
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    try:
        components = import_nodes_components_from_csv(file)
        result = import_and_create_nodes(components)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/import-edges', methods=['POST'])
@swag_from({
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'CSV file with columns: source, target, type_of_relation. The target column can contain multiple IDs separated by semicolons (;) to create multiple relationships from a single source.'
        }
    ],
    'responses': {
        200: {
            'description': 'List of imported edges',
            'schema': {
                'type': 'array',
                'items': {'type': 'object'}
            }
        },
        201: {
            'description': 'Relationships created in Neo4j',
            'schema': {
                'type': 'object',
                'properties': {
                    'created': {'type': 'integer', 'description': 'Number of relationships created'},
                    'updated': {'type': 'integer', 'description': 'Number of relationships updated'},
                    'errors': {'type': 'integer', 'description': 'Number of errors'},
                    'details': {'type': 'array', 'description': 'Details of each relationship operation'}
                }
            }
        },
        400: {'description': 'Validation or file error'}
    }
})
def import_edges():
    """
    Import edges from a CSV file. The CSV must have columns:
    source, target, type_of_relation
    
    The target column can contain multiple IDs separated by semicolons (;).
    For example, "1,2;3;4,CONNECTS_TO" will create relationships from node 1 to nodes 2, 3, and 4.
    
    Always creates relationships in Neo4j. Only source and target are required.
    Returns:
        JSON result of created/updated edges or error message.
    """
    from app.services import import_edges_from_csv, import_and_create_edges
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    
    current_app.logger.info("Iniciando importación de edges")
    
    if 'file' not in request.files:
        current_app.logger.error("No se encontró archivo en la petición")
        return jsonify({'error': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        current_app.logger.error("Archivo vacío en la petición")
        return jsonify({'error': 'No selected file'}), 400
        
    current_app.logger.info(f"Procesando archivo: {file.filename}")
    
    try:
        edges = import_edges_from_csv(file)
        current_app.logger.info(f"Se leyeron {len(edges)} edges del CSV")
        
        if not edges:
            return jsonify({'error': 'No valid edges found in the file'}), 400
            
        result = import_and_create_edges(edges)
        current_app.logger.info(f"Resultado: {result}")
        return jsonify(result), 201
    except ValueError as e:
        current_app.logger.error(f"Error en importación: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500
