"""
Script para probar la importación y creación de nodos en Neo4j.
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

def test_import_from_csv():
    """Test importing nodes from CSV directly to Neo4j"""
    # Usar las mismas variables de entorno que usa la app
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "test1234")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    
    # CSV de prueba
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv", "nodes_clean.csv")
    
    logger.info(f"Leyendo CSV: {csv_path}")
    
    # Leer CSV
    components = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            # Leer la primera línea para determinar el delimitador y saltarla
            first_line = file.readline()
            delimiter = ',' if ',' in first_line else (';' if ';' in first_line else '\t')
            
            reader = csv.reader(file, delimiter=delimiter)
            required_fields = [
                'id', 'label', 'component_type', 'category', 'location',
                'technology', 'host', 'description', 'interface'
            ]
            
            for i, row in enumerate(reader, start=2):  # start=2 porque la línea 1 es el header
                if not row or all(not cell.strip() for cell in row):
                    continue
                    
                component_dict = {field: row[idx].strip() if idx < len(row) and row[idx] is not None else '' 
                                 for idx, field in enumerate(required_fields)}
                
                if not component_dict['id']:
                    logger.warning(f"Row {i}: Missing id, skipping row.")
                    continue
                    
                components.append(component_dict)
                logger.info(f"Componente leído: {component_dict}")
                
    except Exception as e:
        logger.error(f"Error leyendo CSV: {e}", exc_info=True)
        return False
        
    logger.info(f"Se leyeron {len(components)} componentes del CSV.")
    
    # Conectar a Neo4j e importar componentes
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info("✅ Conexión a Neo4j establecida.")
        
        created = 0
        skipped = 0
        errors = 0
        
        with driver.session(database=database) as session:
            for i, comp_dict in enumerate(components):
                try:
                    # Verificar si el componente existe
                    result = session.run(
                        "MATCH (c:Component {id: $id}) RETURN c", 
                        id=comp_dict['id']
                    ).single()
                    
                    if result:
                        logger.info(f"Componente {comp_dict['id']} ya existe, saltando.")
                        skipped += 1
                        continue
                    
                    # Crear componente
                    logger.info(f"Creando componente {i+1}/{len(components)}: {comp_dict['id']}")
                    
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
                        **comp_dict
                    ).single()
                    
                    if result:
                        created += 1
                        logger.info(f"✅ Componente creado: {comp_dict['id']}")
                    else:
                        errors += 1
                        logger.error(f"❌ Error al crear componente: {comp_dict['id']} - No se devolvió resultado")
                        
                except Exception as e:
                    errors += 1
                    logger.error(f"❌ Error al procesar componente {comp_dict.get('id')}: {str(e)}", exc_info=True)
                    
        logger.info(f"Resultados: {created} creados, {skipped} saltados, {errors} errores")
        
        # Verificar cuántos nodos Component existen ahora
        with driver.session(database=database) as session:
            count = session.run("MATCH (c:Component) RETURN count(c) as count").single()
            logger.info(f"✅ Número de nodos Component existentes: {count['count']}")
        
        driver.close()
        
        return created > 0
        
    except Exception as e:
        logger.error(f"Error en la conexión o importación: {str(e)}", exc_info=True)
        return False
        
if __name__ == "__main__":
    success = test_import_from_csv()
    if success:
        print("\n✅ Importación de componentes exitosa.")
    else:
        print("\n❌ Falló la importación. Revise los logs para más detalles.")
