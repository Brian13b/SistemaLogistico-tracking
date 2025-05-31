import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from app.config import settings

logger = logging.getLogger(__name__)

async def send_to_backend(data: dict) -> bool:
    """
    Versión robusta para conexión a backend a través de ngrok
    """
    if not data:
        logger.debug("Ignorando datos no GPS")
        return False

    payload = {
        "device_id": data["device_id"],
        "lat": round(float(data["lat"]), 6),
        "lng": round(float(data["lng"]), 6),
        "speed": int(data["speed"]),
        "course": int(data["course"]),
        "altitude": int(data.get("altitude", 0)),
        "accuracy": int(data.get("accuracy", 5)),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "GT06-Tracker-Server/1.0"
    }

    connector = aiohttp.TCPConnector(
        ssl=settings.NGROK_VERIFY_SSL,
        force_close=True
    )

    for attempt in range(3):  # 3 intentos
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    settings.BACKEND_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=settings.BACKEND_TIMEOUT)
                ) as response:
                    
                    if response.status == 201:
                        logger.info("Datos enviados exitosamente al backend")
                        return True
                    
                    error_detail = await response.text()
                    logger.error(f"Intento {attempt+1} fallido. Status: {response.status}. Error: {error_detail}")
                    
                    # No reintentar para errores 4xx (excepto 429)
                    if 400 <= response.status < 500 and response.status != 429:
                        break

        except asyncio.TimeoutError:
            logger.error(f"Timeout en intento {attempt+1} (>{settings.BACKEND_TIMEOUT}s)")
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Error de conexión en intento {attempt+1}: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado en intento {attempt+1}: {str(e)}")
        
        if attempt < 2:  # Esperar solo entre intentos
            await asyncio.sleep(1)
    
    logger.error(f"Fallo después de 3 intentos. Payload no enviado: {payload}")
    return False