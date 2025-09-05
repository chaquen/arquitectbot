from flask import Blueprint, request, jsonify, current_app
import json
from app.application.component_service import ComponentService
from flasgger import swag_from
from app.infrastructure.neo4j_generic_repository import Neo4jGenericRepository
from app.domain.graph_model import canonical_label

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

# -------- Nuevo: Importar modelo JSON --------
@bp.route('/import-model-json', methods=['POST'])
@swag_from({
    'consumes': ['application/json', 'multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'Archivo JSON con el modelo completo (alternativa a enviar JSON en el body)'
        }
    ],
    'responses': {
        201: {'description': 'Modelo importado'},
        400: {'description': 'Entrada no válida'}
    }
})
def import_model_json():
    """
    Importa el modelo completo desde un JSON en el body o un archivo subido (campo 'file').
    Crea nodos: Component, Host, Metric, Attribute; y relaciones: DESPLIEGA, EJECUTA, EXPONE, IMPACTA.
    """
    from app.application.model_import_service import ModelImportService
    data = None
    if 'file' in request.files:
        file = request.files['file']
        try:
            data = json.loads(file.read().decode('utf-8'))
        except Exception:
            return jsonify({"error": "Archivo JSON inválido"}), 400
    else:
        data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No se recibió JSON (body o archivo)"}), 400

    svc = ModelImportService()
    try:
        svc.ensure_constraints()
        stats = svc.import_model(data)
        return jsonify(stats), 201
    finally:
        svc.close()

# -------- Nuevo: Limpiar base (solo desarrollo) --------
@bp.route('/admin/reset-graph', methods=['POST'])
@swag_from({'responses': {200: {'description': 'Grafo limpiado'}}})
def reset_graph():
    """Elimina todos los nodos y relaciones. Uso de desarrollo/QA."""
    from app.infrastructure.neo4j_generic_repository import Neo4jGenericRepository
    repo = Neo4jGenericRepository()
    try:
        with repo.driver.session(database=repo.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
        return jsonify({"status": "ok"}), 200
    finally:
        repo.close()

# -------- Nuevos endpoints de lectura por tipo de nodo --------
@bp.route('/atributos', methods=['GET'])
@swag_from({
    'tags': ['Atributos'],
    'responses': {200: {'description': 'Lista de atributos'}}
})
def list_atributos():
    repo = Neo4jGenericRepository()
    try:
        nodes = repo.fetch_nodes('Attribute')
        return jsonify([dict(n) for n in nodes]), 200
    finally:
        repo.close()

# CRUD atributos
@bp.route('/atributos/<name>', methods=['GET'])
@swag_from({
    'tags': ['Atributos'],
    'parameters': [{'name': 'name', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {200: {'description': 'Atributo encontrado'}, 404: {'description': 'No encontrado'}}
})
def get_atributo(name):
    repo = Neo4jGenericRepository()
    try:
        node = repo.get_node('Attribute', 'name', name)
        if node:
            return jsonify(node), 200
        return jsonify({'error': 'No encontrado'}), 404
    finally:
        repo.close()

@bp.route('/atributos', methods=['POST'])
@swag_from({
    'tags': ['Atributos'],
    'parameters': [{
        'name': 'body', 'in': 'body', 'required': True,
        'schema': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}
    }],
    'responses': {201: {'description': 'Atributo creado'}, 400: {'description': 'Error de validación'}}
})
def create_atributo():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name requerido'}), 400
    repo = Neo4jGenericRepository()
    try:
        repo.merge_node('Attribute', 'name', name, data)
        return jsonify({'name': name, **data}), 201
    finally:
        repo.close()

@bp.route('/atributos/<name>', methods=['PUT'])
@swag_from({
    'tags': ['Atributos'],
    'parameters': [
        {'name': 'name', 'in': 'path', 'type': 'string', 'required': True},
        {'name': 'body', 'in': 'body', 'schema': {'type': 'object'}}
    ],
    'responses': {200: {'description': 'Atributo actualizado'}, 404: {'description': 'No encontrado'}}
})
def update_atributo(name):
    data = request.get_json() or {}
    repo = Neo4jGenericRepository()
    try:
        updated = repo.update_node('Attribute', 'name', name, data)
        if updated:
            return jsonify(updated), 200
        return jsonify({'error': 'No encontrado'}), 404
    finally:
        repo.close()

@bp.route('/atributos/<name>', methods=['DELETE'])
@swag_from({
    'tags': ['Atributos'],
    'parameters': [{'name': 'name', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {204: {'description': 'Atributo eliminado'}, 404: {'description': 'No encontrado'}}
})
def delete_atributo(name):
    repo = Neo4jGenericRepository()
    try:
        ok = repo.delete_node('Attribute', 'name', name)
        return ('', 204) if ok else (jsonify({'error': 'No encontrado'}), 404)
    finally:
        repo.close()

@bp.route('/hosts', methods=['GET'])
@swag_from({'tags': ['Hosts'], 'responses': {200: {'description': 'Lista de hosts'}}})
def list_hosts():
    repo = Neo4jGenericRepository()
    try:
        nodes = repo.fetch_nodes('Host')
        return jsonify([dict(n) for n in nodes]), 200
    finally:
        repo.close()

@bp.route('/hosts/<name>', methods=['GET'])
@swag_from({'tags': ['Hosts'], 'parameters': [{'name': 'name','in':'path','type':'string','required':True}], 'responses': {200: {'description': 'Host encontrado'}, 404: {'description': 'No encontrado'}}})
def get_host(name):
    repo = Neo4jGenericRepository()
    try:
        node = repo.get_node('Host', 'name', name)
        return (jsonify(node), 200) if node else (jsonify({'error': 'No encontrado'}), 404)
    finally:
        repo.close()

@bp.route('/hosts', methods=['POST'])
@swag_from({'tags': ['Hosts'], 'parameters': [{'name': 'body','in':'body','required':True,'schema':{'type':'object','properties':{'name':{'type':'string'}},'required':['name']}}], 'responses': {201: {'description': 'Host creado'}, 400: {'description': 'Error validación'}}})
def create_host():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name requerido'}), 400
    repo = Neo4jGenericRepository()
    try:
        repo.merge_node('Host', 'name', name, data)
        return jsonify({'name': name, **data}), 201
    finally:
        repo.close()

@bp.route('/hosts/<name>', methods=['PUT'])
@swag_from({'tags': ['Hosts'], 'parameters': [{'name':'name','in':'path','type':'string','required':True},{'name':'body','in':'body','schema':{'type':'object'}}], 'responses': {200: {'description': 'Host actualizado'}, 404: {'description': 'No encontrado'}}})
def update_host(name):
    data = request.get_json() or {}
    repo = Neo4jGenericRepository()
    try:
        updated = repo.update_node('Host', 'name', name, data)
        return (jsonify(updated), 200) if updated else (jsonify({'error': 'No encontrado'}), 404)
    finally:
        repo.close()

@bp.route('/hosts/<name>', methods=['DELETE'])
@swag_from({'tags': ['Hosts'], 'parameters': [{'name':'name','in':'path','type':'string','required':True}], 'responses': {204: {'description': 'Host eliminado'}, 404: {'description': 'No encontrado'}}})
def delete_host(name):
    repo = Neo4jGenericRepository()
    try:
        ok = repo.delete_node('Host', 'name', name)
        return ('', 204) if ok else (jsonify({'error': 'No encontrado'}), 404)
    finally:
        repo.close()

@bp.route('/metricas', methods=['GET'])
@swag_from({'tags': ['Metricas'], 'responses': {200: {'description': 'Lista de métricas'}}})
def list_metricas():
    repo = Neo4jGenericRepository()
    try:
        nodes = repo.fetch_nodes('Metric')
        return jsonify([dict(n) for n in nodes]), 200
    finally:
        repo.close()

@bp.route('/metricas/<name>', methods=['GET'])
@swag_from({'tags': ['Metricas'], 'parameters': [{'name':'name','in':'path','type':'string','required':True}], 'responses': {200: {'description': 'Métrica encontrada'}, 404: {'description': 'No encontrada'}}})
def get_metrica(name):
    repo = Neo4jGenericRepository()
    try:
        node = repo.get_node('Metric', 'name', name)
        return (jsonify(node), 200) if node else (jsonify({'error': 'No encontrado'}), 404)
    finally:
        repo.close()

@bp.route('/metricas', methods=['POST'])
@swag_from({'tags': ['Metricas'], 'parameters': [{'name':'body','in':'body','required':True,'schema':{'type':'object','properties':{'name':{'type':'string'},'sla':{'type':'number'}},'required':['name']}}], 'responses': {201: {'description': 'Métrica creada'}, 400: {'description': 'Error validación'}}})
def create_metrica():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name requerido'}), 400
    repo = Neo4jGenericRepository()
    try:
        repo.merge_node('Metric', 'name', name, data)
        return jsonify({'name': name, **data}), 201
    finally:
        repo.close()

@bp.route('/metricas/<name>', methods=['PUT'])
@swag_from({'tags': ['Metricas'], 'parameters': [{'name':'name','in':'path','type':'string','required':True},{'name':'body','in':'body','schema':{'type':'object'}}], 'responses': {200: {'description': 'Métrica actualizada'}, 404: {'description': 'No encontrada'}}})
def update_metrica(name):
    data = request.get_json() or {}
    repo = Neo4jGenericRepository()
    try:
        updated = repo.update_node('Metric', 'name', name, data)
        return (jsonify(updated), 200) if updated else (jsonify({'error': 'No encontrado'}), 404)
    finally:
        repo.close()

@bp.route('/metricas/<name>', methods=['DELETE'])
@swag_from({'tags': ['Metricas'], 'parameters': [{'name':'name','in':'path','type':'string','required':True}], 'responses': {204: {'description': 'Métrica eliminada'}, 404: {'description': 'No encontrada'}}})
def delete_metrica(name):
    repo = Neo4jGenericRepository()
    try:
        ok = repo.delete_node('Metric', 'name', name)
        return ('', 204) if ok else (jsonify({'error': 'No encontrado'}), 404)
    finally:
        repo.close()

# Alias español para components
@bp.route('/componentes', methods=['GET'])
@swag_from({'tags': ['Componentes (alias)'], 'responses': {200: {'description': 'Lista de componentes'}}})
def list_componentes_es():
    return get_components()

@bp.route('/componentes/<component_id>', methods=['GET'])
@swag_from({'tags': ['Componentes (alias)'], 'parameters': [{'name':'component_id','in':'path','type':'string','required':True}], 'responses': {200: {'description': 'Componente encontrado'}, 404: {'description': 'No encontrado'}}})
def get_componente_es(component_id):
    return get_component(component_id)

@bp.route('/componentes', methods=['POST'])
@swag_from({'tags': ['Componentes (alias)'], 'responses': {201: {'description': 'Componente creado'}, 400: {'description': 'Error validación'}}})
def create_componente_es():
    return create_component()

@bp.route('/componentes/<component_id>', methods=['PUT'])
@swag_from({'tags': ['Componentes (alias)'], 'responses': {200: {'description': 'Componente actualizado'}, 404: {'description': 'No encontrado'}}})
def update_componente_es(component_id):
    return update_component(component_id)

@bp.route('/componentes/<component_id>', methods=['DELETE'])
@swag_from({'tags': ['Componentes (alias)'], 'responses': {204: {'description': 'Componente eliminado'}, 404: {'description': 'No encontrado'}}})
def delete_componente_es(component_id):
    return delete_component(component_id)

# Ya existe /components -> reutiliza

@bp.route('/relaciones', methods=['GET'])
@swag_from({'tags': ['Relaciones'], 'responses': {200: {'description': 'Lista de relaciones'}}})
def list_relaciones():
    repo = Neo4jGenericRepository()
    try:
        rels = repo.fetch_relationships()
        return jsonify(rels), 200
    finally:
        repo.close()

@bp.route('/relaciones', methods=['POST'])
@swag_from({'tags': ['Relaciones'], 'parameters': [{'name':'body','in':'body','required':True,'schema':{'type':'object','properties':{'from':{'type':'object'},'to':{'type':'object'},'type':{'type':'string'},'props':{'type':'object'}},'required':['from','to','type']}}], 'responses': {201: {'description': 'Relación creada'}, 400: {'description': 'Error'}}})
def create_relacion():
    data = request.get_json() or {}
    from_spec = data.get('from') or data.get('from_')
    to_spec = data.get('to')
    rel_type = data.get('type') or 'RELATES'
    props = data.get('props') or {}
    if not (from_spec and to_spec and rel_type):
        return jsonify({'error': 'from/to/type requeridos'}), 400
    try:
        repo = Neo4jGenericRepository()
        try:
            repo.merge_relationship(
                canonical_label(from_spec.get('label', 'Component')),
                from_spec.get('key', 'name'),
                from_spec.get('value'),
                canonical_label(to_spec.get('label', 'Component')),
                to_spec.get('key', 'name'),
                to_spec.get('value'),
                rel_type,
                props
            )
            return jsonify({'message': 'Relación creada'}), 201
        finally:
            repo.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    
