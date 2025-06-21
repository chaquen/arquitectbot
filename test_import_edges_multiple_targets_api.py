"""
Script para probar la importación de relaciones con múltiples targets a través de la API Flask.
"""
import os
import sys
import logging
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_import_edges_multiple_targets_api():
    """Test importing edges with multiple targets via the Flask API endpoint"""
      # URL de la API Flask (asumiendo que se ejecuta localmente)
    api_url = os.environ.get("API_URL", "http://localhost:5000")
    import_endpoint = f"{api_url}/import-edges"
      # CSV de prueba con múltiples targets
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv", "edges_multiple_targets.csv")
    
    logger.info(f"Usando archivo CSV: {csv_path}")
    logger.info(f"Endpoint de importación: {import_endpoint}")
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(csv_path):
            logger.error(f"❌ Archivo CSV no encontrado: {csv_path}")
            return False
              # Verificar si la API está disponible - usando OPTIONS en el endpoint de importación
        try:
            health_check = requests.options(import_endpoint)
            if health_check.status_code >= 400:
                logger.error(f"❌ El endpoint de importación no está disponible. Status code: {health_check.status_code}")
                return False
            logger.info(f"✅ El endpoint de importación está disponible. Métodos permitidos: {health_check.headers.get('Allow', 'Unknown')}")
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ No se pudo conectar a la API en {api_url}")
            logger.info("Asegúrate de que la aplicación Flask esté en ejecución")
            return False
            
        # Enviar el archivo al endpoint
        with open(csv_path, 'rb') as file:
            files = {'file': (os.path.basename(csv_path), file, 'text/csv')}
            logger.info(f"Enviando archivo {os.path.basename(csv_path)} a {import_endpoint}...")
            response = requests.post(import_endpoint, files=files)
            
        # Verificar la respuesta
        if response.status_code == 201:
            result = response.json()
            logger.info(f"✅ Importación exitosa: {result}")
            
            created = result.get('created', 0)
            updated = result.get('updated', 0)
            errors = result.get('errors', 0)
            
            logger.info(f"Resultados: {created} creadas, {updated} actualizadas, {errors} errores")
            
            if created > 0 or updated > 0:
                logger.info("✅ La importación de relaciones con múltiples targets vía API fue exitosa")
                return True
            else:
                logger.warning("⚠️ No se crearon o actualizaron relaciones")
                return False
        else:
            logger.error(f"❌ Error en la importación. Status code: {response.status_code}")
            logger.error(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("=== Prueba de importación de edges con múltiples targets via API ===")
    success = test_import_edges_multiple_targets_api()
    logger.info("=== Resultado de la prueba: %s ===", "ÉXITO" if success else "FALLO")
    sys.exit(0 if success else 1)
