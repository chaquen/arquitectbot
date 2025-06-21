import csv
from typing import List, Dict, Any
from flask import current_app
from werkzeug.datastructures import FileStorage
from app.domain.component import Component
from app.infrastructure.neo4j_repository import Neo4jComponentRepository
import re

def _detect_delimiter(header_line: str) -> str:
    """
    Detects the delimiter used in the CSV file based on the header line.
    """
    if '\t' in header_line:
        return '\t'
    elif ';' in header_line:
        return ';'
    else:
        return ','

def import_nodes_components_from_csv(file: FileStorage) -> List[Dict[str, Any]]:
    """
    Reads a CSV file with component nodes and returns a list of dictionaries.
    Only 'id' is required. All other fields will default to '' if missing.
    Args:
        file (FileStorage): The uploaded CSV file.
    Returns:
        List[Dict[str, Any]]: List of component nodes as dictionaries.
    Raises:
        ValueError: If the CSV is invalid.
    """
    required_fields = [
        'id', 'label', 'component_type', 'category', 'location',
        'technology', 'host', 'description', 'interface'
    ]
    components = []
    try:
        file.stream.seek(0)
        first_line = file.stream.readline().decode('utf-8')  # Read and ignore header
        delimiter = _detect_delimiter(first_line)
        reader = csv.reader((line.decode('utf-8') for line in file.stream), delimiter=delimiter)
        for i, row in enumerate(reader, start=2):  # start=2 because header is line 1
            if not row or all(not cell.strip() for cell in row):
                continue
            # Map values by order, fill missing with ''
            component_dict = {field: row[idx].strip() if idx < len(row) and row[idx] is not None else '' for idx, field in enumerate(required_fields)}
            if not component_dict['id']:
                current_app.logger.warning(f"Row {i}: Missing id, skipping row.")
                continue
            components.append(component_dict)
    except Exception as e:
        current_app.logger.error(f"Error reading CSV: {e}")
        raise ValueError(f"Invalid CSV file: {e}")
    return components

def import_edges_from_csv(file: FileStorage) -> List[Dict[str, Any]]:
    """
    Reads a CSV file with edges and returns a list of dictionaries.
    Args:
        file (FileStorage): The uploaded CSV file.
    Returns:
        List[Dict[str, Any]]: List of edges as dictionaries.
    Raises:
        ValueError: If the CSV is invalid or missing required columns (only source y target son obligatorios).
    """
    required_fields = ['source', 'target', 'type_of_relation']
    edges = []
    try:
        file.stream.seek(0)
        first_line = file.stream.readline().decode('utf-8-sig').strip()  # Read header
        delimiter = _detect_delimiter(first_line)
        
        # Reiniciar y leer todo el archivo
        file.stream.seek(0)
        
        # Crear un lector CSV con el delimitador detectado
        reader = csv.reader((line.decode('utf-8-sig') for line in file.stream), delimiter=delimiter)
        
        # Leer el encabezado y determinar los índices de columnas
        header = next(reader)
        header = [h.strip().lower() for h in header]
        
        # Buscar los índices de las columnas requeridas
        source_idx = header.index('source') if 'source' in header else 0
        target_idx = header.index('target') if 'target' in header else 1
        type_idx = -1
        if 'type_of_relation' in header:
            type_idx = header.index('type_of_relation')
        elif 'type' in header:
            type_idx = header.index('type')
        
        current_app.logger.info(f"CSV header: {header}")
        current_app.logger.info(f"Índices detectados: source={source_idx}, target={target_idx}, type_of_relation={type_idx}")
        
        # Leer las filas
        for i, row in enumerate(reader, start=2):  # start=2 porque la línea 1 es el header
            if not row or len(row) == 0 or all(not cell.strip() for cell in row):
                current_app.logger.warning(f"Row {i}: Fila vacía, saltando.")
                continue
            
            # Extraer campos
            source = row[source_idx].strip() if source_idx < len(row) else ''
            target = row[target_idx].strip() if target_idx < len(row) else ''
            rel_type = row[type_idx].strip() if type_idx >= 0 and type_idx < len(row) else 'CONNECTS_TO'
            
            if not source or not target:
                current_app.logger.warning(f"Row {i}: Faltan source o target, saltando fila.")
                continue
                
            edge_dict = {
                'source': source,
                'target': target,
                'type_of_relation': rel_type
            }
            
            edges.append(edge_dict)
            current_app.logger.debug(f"Edge leído: {edge_dict}")
            
    except Exception as e:
        current_app.logger.error(f"Error reading CSV: {e}", exc_info=True)
        raise ValueError(f"Invalid CSV file: {e}")
        
    current_app.logger.info(f"Se leyeron {len(edges)} edges del CSV.")
    return edges

def import_and_create_nodes(components: List[Dict[str, Any]]) -> dict:
    """
    Crea nodos de componentes en Neo4j a partir de una lista de diccionarios.
    Args:
        components (List[Dict[str, Any]]): Lista de componentes leídos del CSV.
    Returns:
        dict: {'created': int, 'skipped': int, 'errors': int, 'details': list}
    """
    current_app.logger.info(f"Iniciando creación de {len(components)} componentes en Neo4j")
    
    repo = Neo4jComponentRepository()
    current_app.logger.info(f"Repositorio Neo4j inicializado")
    
    created = 0
    skipped = 0
    errors = 0
    details = []
    
    # Verificar si la base de datos está accesible
    try:
        # Intentamos una operación simple para verificar la conexión
        with repo.driver.session(database=repo.database) as session:
            result = session.run("RETURN 1 as test").single()
            if result:
                current_app.logger.info(f"Conexión a Neo4j verificada: {result['test']}")
    except Exception as e:
        current_app.logger.error(f"Error al conectar con Neo4j: {str(e)}", exc_info=True)
        repo.close()
        return {'created': 0, 'skipped': 0, 'errors': len(components), 'details': [{'error': f"Error de conexión a Neo4j: {str(e)}"}]}
    
    # Crear los nodos
    for i, comp in enumerate(components):
        try:
            current_app.logger.debug(f"Procesando componente {i+1}/{len(components)}: {comp}")
            component = Component(**comp)
            current_app.logger.debug(f"Objeto componente creado: id={component.id}")
            
            # Verificar si existe directamente con una consulta simple
            with repo.driver.session(database=repo.database) as session:
                existing_check = session.run(
                    "MATCH (c:Component {id: $id}) RETURN count(c) as count", 
                    id=component.id
                ).single()
                
                exists = existing_check and existing_check["count"] > 0
                
                if exists:
                    current_app.logger.info(f"Componente ya existe, ID: {component.id}")
                    skipped += 1
                    details.append({'id': component.id, 'status': 'skipped (already exists)'})
                    continue
                
                # Crear el componente directamente en la sesión
                current_app.logger.info(f"Creando componente con ID: {component.id}")
                result = session.run(
                    """
                    CREATE (c:Component {
                        id: $id,
                        label: $label,
                        component_type: $component_type,
                        category: $category,
                        location: $location,
                        technology: $technology,
                        host: $host,
                        description: $description,
                        interface: $interface
                    })
                    RETURN c
                    """,
                    id=component.id,
                    label=component.label,
                    component_type=component.component_type,
                    category=component.category,
                    location=component.location,
                    technology=component.technology,
                    host=component.host,
                    description=component.description,
                    interface=component.interface
                ).single()
                
                if result:
                    current_app.logger.info(f"Componente creado: {component.id}")
                    created += 1
                    details.append({'id': component.id, 'status': 'created'})
                else:
                    current_app.logger.error(f"No se pudo crear el componente: {component.id}")
                    errors += 1
                    details.append({'id': component.id, 'status': 'error: no result returned'})
                
        except Exception as e:
            current_app.logger.error(f"Error al crear componente {comp.get('id', 'unknown')}: {str(e)}", exc_info=True)
            errors += 1
            details.append({'id': comp.get('id', None), 'status': f'error: {str(e)}'})
    
    current_app.logger.info(f"Resultado final: creados={created}, omitidos={skipped}, errores={errors}")
    repo.close()
    return {'created': created, 'skipped': skipped, 'errors': errors, 'details': details}

def import_and_create_edges(edges: List[Dict[str, Any]]) -> dict:
    """
    Crea relaciones CONNECTS_TO en Neo4j a partir de una lista de diccionarios.
    Args:
        edges (List[Dict[str, Any]]): Lista de edges leídos del CSV.
    Returns:
        dict: {'created': int, 'updated': int, 'errors': int, 'details': list}
    """
    current_app.logger.info(f"Iniciando creación de {len(edges)} relaciones en Neo4j")
    
    repo = Neo4jComponentRepository()
    current_app.logger.info(f"Repositorio Neo4j inicializado")
    
    created = 0
    updated = 0
    errors = 0
    details = []
    
    # Verificar si la base de datos está accesible
    try:
        # Intentamos una operación simple para verificar la conexión
        with repo.driver.session(database=repo.database) as session:
            result = session.run("RETURN 1 as test").single()
            if result:
                current_app.logger.info(f"Conexión a Neo4j verificada: {result['test']}")
                
            # Verificar si hay nodos Component existentes
            count = session.run("MATCH (c:Component) RETURN count(c) as count").single()
            current_app.logger.info(f"Número de nodos Component existentes: {count['count']}")
            
            if count['count'] == 0:
                current_app.logger.error("No hay nodos Component en la base de datos. Primero debes importar nodos.")
                repo.close()
                return {'created': 0, 'updated': 0, 'errors': len(edges), 'details': [{'error': "No hay nodos en la base de datos"}]}
    except Exception as e:
        current_app.logger.error(f"Error al conectar con Neo4j: {str(e)}", exc_info=True)
        repo.close()
        return {'created': 0, 'updated': 0, 'errors': len(edges), 'details': [{'error': f"Error de conexión a Neo4j: {str(e)}"}]}
    
    for i, edge in enumerate(edges):
        source = edge['source']
        target = edge['target']
        rel_type = edge.get('type_of_relation', 'CONNECTS_TO')
        
        try:
            current_app.logger.info(f"Procesando relación {i+1}/{len(edges)}: {source} -> {target} ({rel_type})")
            
            with repo.driver.session(database=repo.database) as session:
                # Verificar si ambos nodos existen
                check_result = session.run(
                    """
                    MATCH (source:Component {id: $source})
                    MATCH (target:Component {id: $target})
                    RETURN count(source) > 0 AND count(target) > 0 as both_exist
                    """,
                    source=source,
                    target=target
                ).single()
                
                if not check_result or not check_result['both_exist']:
                    errors += 1
                    current_app.logger.error(f"No se encontraron los nodos para la relación: {source} -> {target}")
                    details.append({'source': source, 'target': target, 'status': 'error: nodes not found'})
                    continue
                
                # Verificar si la relación ya existe
                exists_check = session.run(
                    """
                    MATCH (source:Component {id: $source})-[r:CONNECTS_TO]->(target:Component {id: $target})
                    RETURN count(r) > 0 as exists
                    """,
                    source=source,
                    target=target
                ).single()
                
                if exists_check and exists_check['exists']:
                    current_app.logger.info(f"La relación ya existe: {source} -> {target}, actualizando propiedades")
                    
                    # Actualizar propiedades
                    update_result = session.run(
                        """
                        MATCH (source:Component {id: $source})-[r:CONNECTS_TO]->(target:Component {id: $target})
                        SET r.type_of_relation = $rel_type
                        RETURN r
                        """,
                        source=source,
                        target=target,
                        rel_type=rel_type
                    ).single()
                    
                    if update_result:
                        updated += 1
                        details.append({'source': source, 'target': target, 'status': 'updated'})
                        current_app.logger.info(f"Relación actualizada: {source} -> {target}")
                    else:
                        errors += 1
                        details.append({'source': source, 'target': target, 'status': 'error: could not update relation'})
                        current_app.logger.error(f"No se pudo actualizar la relación: {source} -> {target}")
                    continue
                
                # Crear la relación
                result = session.run(
                    """
                    MATCH (source:Component {id: $source})
                    MATCH (target:Component {id: $target})
                    CREATE (source)-[r:CONNECTS_TO {type_of_relation: $rel_type}]->(target)
                    RETURN r
                    """,
                    source=source,
                    target=target,
                    rel_type=rel_type
                ).single()
                
                if result:
                    created += 1
                    details.append({'source': source, 'target': target, 'status': 'created'})
                    current_app.logger.info(f"Relación creada: {source} -> {target}")
                else:
                    errors += 1
                    details.append({'source': source, 'target': target, 'status': 'error: could not create relation'})
                    current_app.logger.error(f"No se pudo crear la relación: {source} -> {target}")
            
        except Exception as e:
            errors += 1
            current_app.logger.error(f"Error al procesar relación {source} -> {target}: {str(e)}", exc_info=True)
            details.append({'source': source, 'target': target, 'status': f'error: {str(e)}'})
    
    current_app.logger.info(f"Resultado final: creados={created}, actualizados={updated}, errores={errors}")
    
    # Verificar cuántas relaciones CONNECTS_TO existen ahora
    try:
        with repo.driver.session(database=repo.database) as session:
            count = session.run("MATCH ()-[r:CONNECTS_TO]->() RETURN count(r) as count").single()
            current_app.logger.info(f"Número de relaciones CONNECTS_TO existentes: {count['count']}")
    except Exception as e:
        current_app.logger.error(f"Error al contar relaciones: {str(e)}")
        
    repo.close()
    return {'created': created, 'updated': updated, 'errors': errors, 'details': details}
