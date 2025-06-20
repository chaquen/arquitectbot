# Architecture Component Management API

Este proyecto es una API REST basada en Flask y Neo4j para la gestión de componentes de arquitectura de despliegue.

## Características

- CRUD de componentes de arquitectura
- Base de datos gráfica Neo4j
- Arquitectura hexagonal (domain, application, interfaces, infrastructure)
- Docker y Docker Compose para despliegue local
- Documentación Swagger en `/apidocs`
- Pruebas automáticas con pytest

## Requisitos previos

- Docker y Docker Compose instalados

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

## Notas

- Para detener los servicios, usa:

    ```bash
    docker-compose down
    ```

- Puedes modificar la contraseña de Neo4j en `docker-compose.yml` si lo deseas.


