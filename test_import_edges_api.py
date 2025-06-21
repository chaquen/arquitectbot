"""
Script para probar la importación de edges a través de la API Flask.
"""
import requests
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_import_edges_via_api():
    """Prueba la importación de edges mediante el endpoint de la API Flask"""
    # URL de la API
    base_url = "http://localhost:5000"
    
    # Archivo CSV de edges
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv", "edges_clean.csv")
    
    if not os.path.exists(csv_path):
        logger.error(f"No se encontró el archivo CSV: {csv_path}")
        return False
      # Verificar que la API esté funcionando
    try:
        response = requests.get(f"{base_url}/components")
        if response.status_code != 200:
            logger.error(f"La API no está respondiendo correctamente: {response.status_code}")
            try:
                logger.error(f"Detalle del error: {response.text}")
            except:
                pass
            return False
        components = response.json()
        logger.info(f"API funcionando. Hay {len(components)} componentes en la base de datos.")
    except Exception as e:
        logger.error(f"Error al conectar con la API: {str(e)}")
        return False
    
    # Importar edges mediante la API
    try:
        logger.info(f"Importando edges desde {csv_path}")
        with open(csv_path, 'rb') as file:
            files = {'file': (os.path.basename(csv_path), file, 'text/csv')}
            response = requests.post(
                f"{base_url}/import-edges",
                files=files
            )
        
        if response.status_code not in [200, 201]:
            logger.error(f"Error en la importación: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        logger.info(f"Resultado de la importación: {result}")
        
        # Verificar resultados
        if result.get('created', 0) > 0 or result.get('updated', 0) > 0:
            logger.info("✅ Importación exitosa.")
            return True
        elif result.get('errors', 0) > 0:
            logger.warning("⚠️ Importación completada con errores.")
            for detail in result.get('details', []):
                if 'error' in detail.get('status', ''):
                    logger.warning(f"  - {detail}")
            return False
        else:
            logger.warning("⚠️ No se importaron edges (posiblemente ya existían).")
            return True
            
    except Exception as e:
        logger.error(f"Error en la importación: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_import_edges_via_api()
    if success:
        print("\n✅ Prueba de importación de edges vía API exitosa.")
    else:
        print("\n❌ Falló la importación vía API. Revise los logs para más detalles.")
