from neo4j import GraphDatabase
from app.domain.component import Component
from app.domain.interface_comunicacion import InterfazComunicacion
from typing import List, Optional
import os

class Neo4jComponentRepository:
    """Repositorio para componentes usando Neo4j como backend."""
    def __init__(self):
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "test1234")
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def create(self, component: Component) -> Component:
        with self.driver.session(database=self.database) as session:
            result = session.write_transaction(self._create_component_with_interfaces, component)
            return result

    @staticmethod
    def _create_component_with_interfaces(tx, component: Component) -> Component:
        # Crear el nodo del componente
        query_comp = """
        CREATE (c:Component {
            nombre: $nombre,
            descripcion: $descripcion,
            tipo: $tipo,
            tecnologia: $tecnologia,
            artefacto: $artefacto,
            nodo_despliegue: $nodo_despliegue,
            puerto_de_despliegue: $puerto_de_despliegue,
            dependencias: $dependencias,
            seguridad: $seguridad,
            escalabilidad: $escalabilidad,
            observabilidad: $observabilidad,
            notas_adicionales: $notas_adicionales,
            id: randomUUID()
        })
        RETURN c
        """
        comp_props = component.to_dict().copy()
        comp_props.pop('id', None)
        interfaces = comp_props.pop('interfaces_comunicacion', [])
        record = tx.run(query_comp, **comp_props).single()
        node = record["c"]
        comp_id = node['id']
        # Crear nodos y relaciones para interfaces de comunicación
        for interfaz in interfaces:
            query_iface = """
            CREATE (i:InterfazComunicacion {
                tipo: $tipo,
                protocolo: $protocolo,
                endpoint: $endpoint,
                puerto: $puerto,
                descripcion: $descripcion,
                id: randomUUID()
            })
            WITH i
            MATCH (c:Component {id: $comp_id})
            CREATE (c)-[:TIENE_INTERFAZ]->(i)
            RETURN i
            """
            tx.run(query_iface, comp_id=comp_id, **interfaz)
        # Consultar el componente con interfaces
        return Neo4jComponentRepository._get_component_with_interfaces(tx, comp_id)

    def get_by_id(self, component_id: str) -> Optional[Component]:
        with self.driver.session(database=self.database) as session:
            return session.read_transaction(self._get_component_with_interfaces, component_id)

    @staticmethod
    def _get_component_with_interfaces(tx, component_id: str) -> Optional[Component]:
        query = """
        MATCH (c:Component {id: $id})
        OPTIONAL MATCH (c)-[:TIENE_INTERFAZ]->(i:InterfazComunicacion)
        RETURN c, collect(i) as interfaces
        """
        result = tx.run(query, id=component_id).single()
        if result:
            cdict = dict(result['c'])
            interfaces = [dict(i) for i in result['interfaces'] if i]
            cdict['interfaces_comunicacion'] = interfaces
            return Component.from_dict(cdict)
        return None

    def get_all(self) -> List[Component]:
        with self.driver.session(database=self.database) as session:
            return session.read_transaction(self._get_all_components_with_interfaces)

    @staticmethod
    def _get_all_components_with_interfaces(tx) -> List[Component]:
        query = """
        MATCH (c:Component)
        OPTIONAL MATCH (c)-[:TIENE_INTERFAZ]->(i:InterfazComunicacion)
        WITH c, collect(i) as interfaces
        RETURN c, interfaces
        """
        result = tx.run(query)
        components = []
        for record in result:
            cdict = dict(record['c'])
            interfaces = [dict(i) for i in record['interfaces'] if i]
            cdict['interfaces_comunicacion'] = interfaces
            components.append(Component.from_dict(cdict))
        return components

    def update(self, component_id: str, data: dict) -> Optional[Component]:
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._update_component, component_id, data)

    @staticmethod
    def _update_component(tx, component_id: str, data: dict) -> Optional[Component]:
        query = """
        MATCH (c:Component {id: $id})
        SET c += $props
        RETURN c
        """
        # Asegurarse de que puerto_de_despliegue esté presente aunque sea None
        if 'puerto_de_despliegue' not in data:
            data['puerto_de_despliegue'] = None
        data.pop('id', None)
        result = tx.run(query, id=component_id, props=data).single()
        if result:
            return Component.from_dict(dict(result['c']))
        return None

    def delete(self, component_id: str) -> bool:
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._delete_component, component_id)

    @staticmethod
    def _delete_component(tx, component_id: str) -> bool:
        query = "MATCH (c:Component {id: $id}) DETACH DELETE c RETURN COUNT(c) as deleted"
        result = tx.run(query, id=component_id).single()
        return result and result['deleted'] > 0
