"""
Script para verificar si la aplicación está mostrando correctamente las relaciones en Neo4j.
Este script genera un informe simple de los nodos y relaciones en la base de datos.
"""
import os
import sys
from neo4j import GraphDatabase
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_neo4j_report():
    """Generate a report of nodes and relationships in Neo4j"""
    # Usar las mismas variables de entorno que usa la app
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "test1234")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    
    try:
        # Conectar a Neo4j
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info("✅ Conexión a Neo4j establecida")
        
        with driver.session(database=database) as session:
            # Contar nodos por etiqueta
            node_count = session.run(
                """
                MATCH (n) 
                RETURN labels(n) as label, count(*) as count
                ORDER BY count DESC
                """
            ).data()
            
            logger.info("=== NODOS EN LA BASE DE DATOS ===")
            for item in node_count:
                logger.info(f"  {item['label']}: {item['count']} nodos")
                
            # Contar relaciones por tipo
            rel_count = session.run(
                """
                MATCH ()-[r]->() 
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
                """
            ).data()
            
            logger.info("\n=== RELACIONES EN LA BASE DE DATOS ===")
            for item in rel_count:
                logger.info(f"  {item['type']}: {item['count']} relaciones")
                
            # Mostrar algunos nodos con sus conexiones
            sample_nodes = session.run(
                """
                MATCH (n:Component)
                RETURN n.id as id, n.label as label, n.component_type as type 
                LIMIT 5
                """
            ).data()
            
            logger.info("\n=== MUESTRA DE NODOS ===")
            for node in sample_nodes:
                logger.info(f"  ID: {node['id']}, Label: {node['label']}, Tipo: {node['type']}")
                
                # Buscar relaciones salientes
                out_relations = session.run(
                    """
                    MATCH (n:Component {id: $id})-[r]->(m)
                    RETURN type(r) as type, m.id as target_id, m.label as target_label
                    """,
                    id=node['id']
                ).data()
                
                if out_relations:
                    logger.info(f"    Relaciones salientes:")
                    for rel in out_relations:
                        logger.info(f"      {rel['type']} -> {rel['target_id']} ({rel['target_label']})")
                
                # Buscar relaciones entrantes
                in_relations = session.run(
                    """
                    MATCH (n:Component {id: $id})<-[r]-(m)
                    RETURN type(r) as type, m.id as source_id, m.label as source_label
                    """,
                    id=node['id']
                ).data()
                
                if in_relations:
                    logger.info(f"    Relaciones entrantes:")
                    for rel in in_relations:
                        logger.info(f"      {rel['type']} <- {rel['source_id']} ({rel['source_label']})")
            
        driver.close()
        logger.info("\n✅ Reporte generado correctamente")
        return True
    
    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = generate_neo4j_report()
    if not success:
        print("\n❌ Error al generar el reporte. Revise los logs para más detalles.")
