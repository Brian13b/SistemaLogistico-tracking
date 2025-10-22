import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from app.config import settings

logger = logging.getLogger(__name__)

async def send_to_backend(data: dict) -> bool:
    """Envía datos al backend con manejo robusto de errores"""
    if not data or 'lat' not in data or 'lng' not in data:
        logger.debug("Datos incompletos ignorados")
        return False

    try:
        # Preparar payload con formato consistente
        payload = {
            "device_id": data["device_id"],
            "lat": data["lat"],
            "lng": data["lng"],
            "speed": data.get("speed", 0),
            "course": data.get("course", 0),
            "altitude": data.get("altitude", 0),
            "accuracy": data.get("accuracy", 5),
            "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat())
        }

        # Construir headers correctamente
        headers = {
            "Content-Type": "application/json"
        }
        
        # Solo añadir Authorization si API_KEY existe y no está vacía
        if settings.API_KEY and settings.API_KEY.strip():
            headers["Authorization"] = f"Bearer {settings.API_KEY.strip()}"

        # logger.debug(f"Enviando al backend - URL: {settings.BACKEND_URL}")
        # logger.debug(f"Headers: {headers}")
        # logger.debug(f"Payload: {payload}")

        async with aiohttp.ClientSession() as session:
            for attempt in range(3):
                try:
                    async with session.post(
                        settings.BACKEND_URL_TRACKING,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=settings.BACKEND_TIMEOUT)
                    ) as response:
                        
                        if response.status == 201:
                            logger.info("Datos enviados correctamente")
                            return True
                            
                        error = await response.text()
                        logger.error(f"Intento {attempt+1} fallido. Status: {response.status}. Error: {error}")
                        
                        if 400 <= response.status < 500:
                            break

                except asyncio.TimeoutError:
                    logger.error(f"Timeout en intento {attempt+1}")
                except Exception as e:
                    logger.error(f"Error en intento {attempt+1}: {str(e)}")
                
                if attempt < 2:
                    await asyncio.sleep(1)
        
        logger.error(f"Fallo después de 3 intentos.")
        return False

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return False