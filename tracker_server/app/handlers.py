import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from app.config import settings

logger = logging.getLogger(__name__)

async def send_to_backend(data: dict) -> bool:
    """Envía datos al backend con manejo robusto de errores"""
    if not data or data.get('type') != 'gps':
        logger.debug("Datos no GPS ignorados")
        return False

    try:
        # Preparar payload con formato consistente
        payload = {
            "device_id": data["device_id"],
            "lat": data["lat"],
            "lng": data["lng"],
            "speed": data["speed"],
            "course": data["course"],
            "altitude": data.get("altitude", 0),
            "accuracy": data.get("accuracy", 5),
            "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat())
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.API_KEY}" if settings.API_KEY else None
        }

        async with aiohttp.ClientSession() as session:
            for attempt in range(3):
                try:
                    async with session.post(
                        settings.BACKEND_URL,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=settings.BACKEND_TIMEOUT)
                    ) as response:
                        
                        if response.status == 201:
                            logger.info("Datos enviados correctamente")
                            return True
                            
                        error = await response.text()
                        logger.error(f"Intento {attempt+1} fallido. Status: {response.status}. Error: {error}")
                        
                        # No reintentar para errores clientes (4xx)
                        if 400 <= response.status < 500:
                            break

                except asyncio.TimeoutError:
                    logger.error(f"Timeout en intento {attempt+1}")
                except Exception as e:
                    logger.error(f"Error en intento {attempt+1}: {str(e)}")
                
                if attempt < 2:
                    await asyncio.sleep(1)
        
        logger.error(f"Fallo después de 3 intentos. Payload: {payload}")
        return False

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return False