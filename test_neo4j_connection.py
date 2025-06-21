"""
Script de diagnóstico para verificar la conexión a Neo4j.
Ejecutar con: python test_neo4j_connection.py
"""
import os
from neo4j import GraphDatabase
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("neo4j").setLevel(logging.DEBUG)

def test_connection():
    """Test direct connection to Neo4j"""
    # Usar las mismas variables de entorno que usa la app
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "test1234")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    
    logger.info(f"Conectando a Neo4j: {uri}, usuario: {user}, database: {database}")
    
    try:
        # Crear driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verificar conexión
        driver.verify_connectivity()
        logger.info("✅ Conexión a Neo4j establecida exitosamente")
        
        # Probar una consulta simple
        with driver.session(database=database) as session:
            result = session.run("RETURN 1 as num").single()
            logger.info(f"✅ Consulta de prueba exitosa: {result['num']}")
            
            # Comprobar si hay algún nodo Component
            count = session.run("MATCH (c:Component) RETURN count(c) as count").single()
            logger.info(f"✅ Número de nodos Component existentes: {count['count']}")
            
            # Intentar crear un nodo de prueba
            test_id = "test_connection_node"
            session.run(
                """
                MERGE (c:TestNode {id: $id})
                ON CREATE SET c.created = timestamp()
                ON MATCH SET c.updated = timestamp()
                RETURN c
                """, 
                id=test_id
            )
            logger.info(f"✅ Nodo de prueba creado/actualizado con ID: {test_id}")
            
            # Verificar que se creó
            test_node = session.run("MATCH (t:TestNode {id: $id}) RETURN t", id=test_id).single()
            if test_node:
                logger.info(f"✅ Nodo de prueba recuperado: {dict(test_node['t'])}")
            else:
                logger.error("❌ No se pudo recuperar el nodo de prueba")
        
        # Cerrar conexión
        driver.close()
        logger.info("Conexión cerrada")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al conectar con Neo4j: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n✅ Conexión a Neo4j verificada correctamente.")
    else:
        print("\n❌ Falló la conexión a Neo4j. Revise los logs para más detalles.")
