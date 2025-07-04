from neo4j import GraphDatabase
from app.domain.component import Component
from typing import List, Optional
import os

class Neo4jComponentRepository:
    """
    Repository for components using Neo4j as backend.
    Handles all persistence and retrieval operations for Component nodes and their relationships.
    """
    def __init__(self):
        """
        Initialize the Neo4j driver and database connection.
        """
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "test1234")
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
        
        import logging
        logging.getLogger("neo4j").setLevel(logging.DEBUG)
        
        from flask import current_app
        current_app.logger.info(f"Conectando a Neo4j: {uri}, usuario: {user}, database: {database}")
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verificar conexión
            self.driver.verify_connectivity()
            current_app.logger.info("Conexión a Neo4j establecida exitosamente")
        except Exception as e:
            current_app.logger.error(f"Error al conectar con Neo4j: {str(e)}")
            raise
            
        self.database = database

    def close(self):
        """
        Close the Neo4j driver connection.
        """
        self.driver.close()

    def create(self, component: Component) -> Component:
        """
        Create a new Component node in the database.
        Args:
            component (Component): The component to persist.
        Returns:
            Component: The created component with its generated ID.
        """
        from flask import current_app
        current_app.logger.info(f"Creando componente en Neo4j: {component.to_dict()}")
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.write_transaction(self._create_component, component)
                current_app.logger.info(f"Componente creado exitosamente: {result.to_dict() if result else None}")
                return result
        except Exception as e:
            current_app.logger.error(f"Error al crear componente en Neo4j: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _create_component(tx, component: Component) -> Component:
        """
        Cypher transaction to create a Component node.
        """
        from flask import current_app
        query = """
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
        """
        current_app.logger.debug(f"Ejecutando query Cypher: {query}")
        current_app.logger.debug(f"Parámetros: {component.to_dict()}")
        
        try:
            record = tx.run(query,
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
            
            if not record:
                current_app.logger.error("La consulta de creación no devolvió resultados")
                return None
                
            node = record["c"]
            current_app.logger.debug(f"Nodo creado en Neo4j: {dict(node)}")
            
            return Component(
                id=node["id"],
                label=node.get("label", ""),
                component_type=node.get("component_type", ""),
                category=node.get("category", ""),
                location=node.get("location", ""),
                technology=node.get("technology", ""),
                host=node.get("host", ""),
                description=node.get("description", ""),
                interface=node.get("interface", "")
            )
        except Exception as e:
            current_app.logger.error(f"Error en la transacción Cypher: {str(e)}", exc_info=True)
            raise

    def get_by_id(self, component_id: str) -> Optional[Component]:
        """
        Retrieve a Component node by its ID.
        Args:
            component_id (str): The unique identifier of the component.
        Returns:
            Optional[Component]: The component if found, else None.
        """
        from flask import current_app
        current_app.logger.debug(f"Buscando componente por ID: {component_id}")
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.read_transaction(self._get_component, component_id)
                current_app.logger.debug(f"Resultado de búsqueda: {result.to_dict() if result else None}")
                return result
        except Exception as e:
            current_app.logger.error(f"Error al buscar componente: {str(e)}")
            raise

    @staticmethod
    def _get_component(tx, component_id: str) -> Optional[Component]:
        """
        Cypher transaction to retrieve a Component node by ID.
        """
        query = "MATCH (c:Component {id: $id}) RETURN c"
        result = tx.run(query, id=component_id).single()
        if result:
            node = result["c"]
            return Component(
                id=node["id"],
                label=node.get("label", ""),
                component_type=node.get("component_type", ""),
                category=node.get("category", ""),
                location=node.get("location", ""),
                technology=node.get("technology", ""),
                host=node.get("host", ""),
                description=node.get("description", ""),
                interface=node.get("interface", "")
            )
        return None

    def get_all(self) -> List[Component]:
        """
        Retrieve all Component nodes from the database.
        Returns:
            List[Component]: List of all components.
        """
        with self.driver.session(database=self.database) as session:
            return session.read_transaction(self._get_all_components)

    @staticmethod
    def _get_all_components(tx) -> List[Component]:
        """
        Cypher transaction to retrieve all Component nodes.
        """
        query = "MATCH (c:Component) RETURN c"
        result = tx.run(query)
        return [Component(
            id=record["c"]["id"],
            label=record["c"].get("label", ""),
            component_type=record["c"].get("component_type", ""),
            category=record["c"].get("category", ""),
            location=record["c"].get("location", ""),
            technology=record["c"].get("technology", ""),
            host=record["c"].get("host", ""),
            description=record["c"].get("description", ""),
            interface=record["c"].get("interface", "")
        ) for record in result]

    def update(self, component_id: str, data: dict) -> Optional[Component]:
        """
        Update a Component node by its ID.
        Args:
            component_id (str): The unique identifier of the component.
            data (dict): Dictionary with updated properties.
        Returns:
            Optional[Component]: The updated component if found, else None.
        """
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._update_component, component_id, data)

    @staticmethod
    def _update_component(tx, component_id: str, data: dict) -> Optional[Component]:
        """
        Cypher transaction to update a Component node by ID.
        """
        query = """
        MATCH (c:Component {id: $id})
        SET c += $props
        RETURN c
        """
        data.pop('id', None)
        result = tx.run(query, id=component_id, props=data).single()
        if result:
            node = result["c"]
            return Component(
                id=node["id"],
                label=node.get("label", ""),
                component_type=node.get("component_type", ""),
                category=node.get("category", ""),
                location=node.get("location", ""),
                technology=node.get("technology", ""),
                host=node.get("host", ""),
                description=node.get("description", ""),
                interface=node.get("interface", "")
            )
        return None

    def delete(self, component_id: str) -> bool:
        """
        Delete a Component node by its ID.
        Args:
            component_id (str): The unique identifier of the component.
        Returns:
            bool: True if deleted, False if not found.
        """
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._delete_component, component_id)

    @staticmethod
    def _delete_component(tx, component_id: str) -> bool:
        """
        Cypher transaction to delete a Component node by ID.
        """
        query = "MATCH (c:Component {id: $id}) DETACH DELETE c RETURN COUNT(c) as deleted"
        result = tx.run(query, id=component_id).single()
        return result and result['deleted'] > 0

    def connect_components(self, id_from: str, id_to: str, props: dict) -> bool:
        """
        Create a CONNECTS_TO relationship between two components.
        Args:
            id_from (str): ID of the source component.
            id_to (str): ID of the target component.
            props (dict): Properties for the relationship.
        Returns:
            bool: True if the connection was created, False otherwise.
        """
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._connect_components, id_from, id_to, props)

    @staticmethod
    def _connect_components(tx, id_from: str, id_to: str, props: dict) -> bool:
        """
        Cypher transaction to create a CONNECTS_TO relationship between two components.
        """
        query = """
        MATCH (a:Component {id: $id_from}), (b:Component {id: $id_to})
        CREATE (a)-[r:CONNECTS_TO $props]->(b)
        RETURN r
        """
        result = tx.run(query, id_from=id_from, id_to=id_to, props=props).single()
        return result is not None
