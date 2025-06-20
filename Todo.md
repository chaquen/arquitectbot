# 🧩 API de Gestión de Componentes de Arquitectura de Despliegue

Este proyecto es una API REST construida con **Python + Flask**, que implementa un **CRUD completo para componentes de arquitectura de despliegue**, conectada a una base de datos **Neo4j**. La solución sigue una **arquitectura hexagonal (puertos y adaptadores)**, está contenedorizada con **Docker Compose** y cuenta con **pruebas automatizadas con cobertura del 100%**.

## 🧱 Características Principales

- Arquitectura Hexagonal / Limpia
- CRUD de Componentes
- Base de datos gráfica con Neo4j
- API REST con Flask
- Docker y Docker Compose
- Pruebas unitarias y de integración (100% de cobertura)
- Validación de datos
- Estructura escalable y mantenible

## 📦 Modelo de Componente

Ejemplo de estructura del objeto:

```json
{
  "nombre": "auth-service",
  "descripcion": "Servicio de autenticación de usuarios",
  "tipo": "Microservicio",
  "tecnologia": "Node.js + Express",
  "artefacto": "auth-service:1.0",
  "nodo_despliegue": "Contenedor Docker en Kubernetes",
  "dependencias": ["user-service", "PostgreSQL"],
  "interfaces_comunicacion": [
    {
      "tipo": "Entrada",
      "protocolo": "HTTP",
      "endpoint": "/login",
      "puerto": 8080,
      "descripcion": "Login de usuarios"
    }
  ],
  "seguridad": ["JWT", "TLS"],
  "escalabilidad": "Replicado con HPA",
  "observabilidad": "Prometheus y Grafana",
  "notas_adicionales": "Pendiente mejorar trazabilidad"
}
```

## 📁 Estructura del Proyecto

```
/app
  /domain          # Entidades de negocio
  /application     # Casos de uso
  /interfaces      # Adaptadores de entrada (Flask)
  /infrastructure  # Conexión a Neo4j, repositorios
/tests             # Pruebas unitarias e integración
Dockerfile
docker-compose.yml
requirements.txt
```

## 🚀 Cómo ejecutar con Docker

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/nombre-repo.git
cd nombre-repo
```

### 2. Levanta los servicios con Docker Compose

```bash
docker-compose up --build
```

Esto levantará:
- API Flask en `http://localhost:5000`
- Neo4j en `http://localhost:7474` (usuario: `neo4j`, contraseña por defecto: `test`)

## 🧪 Pruebas y Cobertura del 100%

### Ejecutar todas las pruebas:

```bash
pytest --cov=app tests/
```

### Ver reporte de cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

Se espera una **cobertura del 100%** en todos los módulos.

## 🧰 Endpoints disponibles

| Método | Ruta                   | Descripción             |
|--------|------------------------|-------------------------|
| GET    | /componentes           | Listar componentes      |
| GET    | /componentes/<id>      | Obtener un componente   |
| POST   | /componentes           | Crear nuevo componente  |
| PUT    | /componentes/<id>      | Actualizar componente   |
| DELETE | /componentes/<id>      | Eliminar componente     |

## 🧠 Recomendaciones

- Usa [Neo4j Desktop](https://neo4j.com/download/) si deseas visualizar la base de datos localmente.
- Documenta los casos de uso en `/application` para facilitar pruebas y mantenimiento.
- Mantén desacopladas las dependencias siguiendo el patrón hexagonal.

## 📄 Licencia

MIT © 2025 - Proyecto académico para Maestría en Ingeniería de Software