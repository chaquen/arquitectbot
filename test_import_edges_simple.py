"""
Script para probar la importación y creación de relaciones entre nodos en Neo4j.
"""
import os
import sys
from neo4j import GraphDatabase
import logging
import csv

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_import_edges_from_csv():
    """Test importing edges from CSV directly to Neo4j"""
    # Usar las mismas variables de entorno que usa la app
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "test1234")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    
    # CSV de prueba
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv", "edges_clean.csv")
    
    logger.info(f"Leyendo CSV de edges: {csv_path}")
    
    # Leer CSV
    edges = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            # Leer la primera línea para determinar el delimitador y el header
            first_line = file.readline().strip()
            delimiter = ',' if ',' in first_line else (';' if ';' in first_line else '\t')
            
            # Reiniciar el puntero y crear un lector con el delimitador correcto
            file.seek(0)
            csv_reader = csv.reader(file, delimiter=delimiter)
            
            # Leer el header y determinar los índices de las columnas requeridas
            header = next(csv_reader)
            header = [h.strip().lower() for h in header]
            
            source_idx = header.index('source') if 'source' in header else 0
            target_idx = header.index('target') if 'target' in header else 1
            type_idx = -1
            if 'type_of_relation' in header:
                type_idx = header.index('type_of_relation')
            elif 'type' in header:
                type_idx = header.index('type')
            
            # Leer las filas y extraer datos
            for i, row in enumerate(csv_reader, start=2):  # start=2 porque la línea 1 es el header
                if not row or all(not cell.strip() for cell in row):
                    logger.warning(f"Row {i}: Fila vacía, saltando.")
                    continue
                
                # Extraer campos
                source = row[source_idx].strip() if source_idx < len(row) else ''
                target = row[target_idx].strip() if target_idx < len(row) else ''
                rel_type = row[type_idx].strip() if type_idx >= 0 and type_idx < len(row) else 'CONNECTS_TO'
                
                if not source or not target:
                    logger.warning(f"Row {i}: Faltan source o target, saltando fila.")
                    continue
                    
                edge_dict = {
                    'source': source,
                    'target': target,
                    'type_of_relation': rel_type
                }
                
                edges.append(edge_dict)
                logger.info(f"Edge leído: {edge_dict}")
                
    except Exception as e:
        logger.error(f"Error leyendo CSV: {e}", exc_info=True)
        return False
        
    logger.info(f"Se leyeron {len(edges)} edges del CSV.")
    
    # Conectar a Neo4j e importar edges
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info("✅ Conexión a Neo4j establecida.")
        
        # Verificar si hay nodos Component existentes
        with driver.session(database=database) as session:
            count = session.run("MATCH (c:Component) RETURN count(c) as count").single()
            logger.info(f"✅ Número de nodos Component existentes: {count['count']}")
            
            if count['count'] == 0:
                logger.error("❌ No hay nodos Component en la base de datos. Primero debes importar nodos.")
                driver.close()
                return False
        
        created = 0
        errors = 0
        
        with driver.session(database=database) as session:
            for i, edge in enumerate(edges):
                source = edge['source']
                target = edge['target']
                rel_type = edge.get('type_of_relation', 'CONNECTS_TO')
                
                try:
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
                        logger.error(f"❌ No se encontraron los nodos para la relación: {source} -> {target}")
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
                        logger.info(f"⚠️ La relación ya existe: {source} -> {target}, actualizando propiedades")
                        
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
                            logger.info(f"✅ Relación actualizada: {source} -> {target}")
                            created += 1
                            continue
                    
                    # Crear la relación
                    logger.info(f"Creando relación {i+1}/{len(edges)}: {source} -> {target} ({rel_type})")
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
                        logger.info(f"✅ Relación creada: {source} -> {target}")
                    else:
                        errors += 1
                        logger.error(f"❌ No se pudo crear la relación: {source} -> {target}")
                        
                except Exception as e:
                    errors += 1
                    logger.error(f"❌ Error al procesar edge {source} -> {target}: {str(e)}", exc_info=True)
                    
        logger.info(f"Resultados: {created} relaciones creadas/actualizadas, {errors} errores")
        
        # Verificar cuántas relaciones CONNECTS_TO existen ahora
        with driver.session(database=database) as session:
            count = session.run("MATCH ()-[r:CONNECTS_TO]->() RETURN count(r) as count").single()
            logger.info(f"✅ Número de relaciones CONNECTS_TO existentes: {count['count']}")
        
        driver.close()
        
        return created > 0
        
    except Exception as e:
        logger.error(f"Error en la conexión o importación: {str(e)}", exc_info=True)
        return False
        
if __name__ == "__main__":
    success = test_import_edges_from_csv()
    if success:
        print("\n✅ Importación de relaciones exitosa.")
    else:
        print("\n❌ Falló la importación. Revise los logs para más detalles.")
