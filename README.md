# Architecture Component Management API

Este proyecto es una API REST basada en Flask y Neo4j para la gestión de componentes de arquitectura de despliegue.

## Características

- CRUD de componentes de arquitectura
- Base de datos gráfica Neo4j
- Arquitectura hexagonal (domain, application, interfaces, infrastructure)
- Docker y Docker Compose para despliegue local
- Documentación Swagger en `/apidocs`
- Pruebas automáticas con pytest
- Importación de nodos y relaciones desde archivos CSV

## Requisitos previos

- Docker y Docker Compose instalados
- Python 3.10+
- Neo4j instalado (para desarrollo local fuera de Docker)
- Bibliotecas Python: flask, neo4j, pytest, flasgger, requests

## Pasos para ejecutar el proyecto

1. Clona el repositorio y navega a la carpeta del proyecto.

2. Construye y levanta los servicios (API y Neo4j) con Docker Compose:

    ```bash
    docker-compose up --build
    ```

3. Accede a la API y Neo4j desde tu navegador:

    - API Flask: [http://localhost:5000](http://localhost:5000)
    - Documentación Swagger: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)
    - Neo4j Browser: [http://localhost:7474](http://localhost:7474) (usuario: `neo4j`, contraseña: `test1234`)

4. Prueba los endpoints desde Swagger o herramientas como Postman:

    - `GET /componentes` - Listar componentes
    - `POST /componentes` - Crear componente
    - `GET /componentes/{id}` - Obtener componente
    - `PUT /componentes/{id}` - Actualizar componente
    - `DELETE /componentes/{id}` - Eliminar componente

## Estructura del Proyecto

- `app/domain/` - Entidades de dominio
- `app/application/` - Casos de uso
- `app/interfaces/` - Adaptadores de entrada (Flask)
- `app/infrastructure/` - Repositorios y conexión a Neo4j
- `tests/` - Pruebas automáticas
- `Dockerfile` y `docker-compose.yml` - Despliegue local

## Pruebas

```bash
pytest
```

## Importación de Datos

La API permite importar componentes y relaciones desde archivos CSV:

- `POST /import-nodes-components` - Importar nodos de componentes desde CSV
- `POST /import-edges` - Importar relaciones entre componentes desde CSV

### Formato de CSV para Nodos

```csv
id,label,component_type,category,location,technology,host,description,interface
1,Servidor Web,Server,Frontend,Local,Nginx,server1.local,Servidor web principal,HTTP
```
Solo el campo `id` es obligatorio, los demás campos tomarán valores vacíos por defecto si no se proporcionan.

### Formato de CSV para Relaciones

```csv
source,target,type_of_relation
1,2,CONNECTS_TO
1,3;4;5,CONNECTS_TO
```
Los campos `source` y `target` son obligatorios y deben corresponder a IDs de nodos existentes. El campo `type_of_relation` es opcional.

El campo `target` puede contener múltiples IDs separados por punto y coma (`;`) para crear varias relaciones desde un solo nodo origen. En el ejemplo anterior, se crearían relaciones desde el nodo 1 hacia los nodos 3, 4 y 5.

## Scripts de Utilidad

El proyecto incluye varios scripts para facilitar la gestión de componentes y depuración:

### Pruebas y Diagnóstico

- `test_neo4j_connection.py` - Prueba la conectividad a la base de datos Neo4j
- `test_import_nodes_simple.py` - Importa nodos directamente desde un archivo CSV
- `test_import_edges_simple.py` - Importa relaciones directamente desde un archivo CSV
- `test_import_nodes_api.py` - Prueba la importación de nodos a través de la API Flask
- `test_import_edges_api.py` - Prueba la importación de relaciones a través de la API Flask
- `generate_neo4j_report.py` - Genera un reporte del estado actual de la base de datos Neo4j

### Ejecución de Scripts

Para ejecutar cualquiera de los scripts de utilidad:

```bash
python <nombre_del_script>.py
```

Ejemplo:
```bash
python test_neo4j_connection.py
```

## Variables de Entorno

Los scripts y la aplicación usan las siguientes variables de entorno:

- `NEO4J_URI` - URI de conexión a Neo4j (default: "bolt://localhost:7687")
- `NEO4J_USER` - Usuario de Neo4j (default: "neo4j")
- `NEO4J_PASSWORD` - Contraseña de Neo4j (default: "test1234")
- `NEO4J_DATABASE` - Nombre de la base de datos Neo4j (default: "neo4j")

## Notas

- Para detener los servicios, usa:

    ```bash
    docker-compose down
    ```

- Los scripts de importación validan los datos antes de insertarlos en la base de datos.
- Las relaciones solo pueden crearse entre nodos existentes.
- Si una relación ya existe, será actualizada con los nuevos atributos proporcionados.


