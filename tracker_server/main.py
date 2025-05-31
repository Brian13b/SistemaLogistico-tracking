import asyncio
import logging
from datetime import datetime, timezone
from app.config import settings
from app.protocol import GT06ProtocolParser
from app.handlers import send_to_backend

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GT06Server:
    def __init__(self):
        self.parser = GT06ProtocolParser()

    async def handle_client(self, reader, writer):
        peername = writer.get_extra_info('peername')
        logger.info(f"Connection from {peername}")

        try:
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=30.0)
                    if not data:
                        logger.info(f"Client {peername} closed connection")
                        break

                    # Validación básica del paquete
                    if len(data) < 8 or data[0] != 0x78 or data[1] != 0x78:
                        logger.warning(f"Invalid packet from {peername}")
                        break

                    protocol = data[3]
                    device_id = data[4:8].hex()

                    # Verificar dispositivo permitido
                    if settings.ALLOWED_DEVICES and device_id not in settings.ALLOWED_DEVICES:
                        logger.warning(f"Unauthorized device: {device_id}")
                        break
                    else:
                        logger.info(f"Processing data from device: {device_id}")

                    # Procesar según tipo de paquete
                    if protocol == 0x01:  # Login
                        packet = self.parser.parse_login(data)
                        logger.info(f"Login from {device_id}")
                        ack = self.parser.create_ack(device_id, data[8])
                        writer.write(ack)
                        
                    elif protocol in (0x10, 0x12, 0x16, 0x22):  # GPS/Alarm
                        packet = self.parser.parse_gps(data)
                        if packet:
                            logger.info(f"GPS data from {device_id}")
                            
                            backend_data = {
                                "device_id": device_id,
                                "lat": packet["lat"],
                                "lng": packet["lng"],
                                "speed": packet["speed"],
                                "course": packet["course"],
                                "altitude": packet.get("altitude", 0),
                                "accuracy": packet.get("accuracy", 5),  # Cambiado de 0 a 5 como valor por defecto
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                            
                            try:
                                success = await send_to_backend(backend_data)
                                if not success:
                                    logger.error(f"Failed to send data to backend. Payload: {backend_data}")
                            except Exception as e:
                                logger.error(f"Critical error sending to backend: {str(e)}")
                                break
                        
                        ack = self.parser.create_ack(device_id, data[8])
                        writer.write(ack)
                        
                    else:
                        logger.warning(f"Unknown protocol: {protocol}")
                        continue

                    await writer.drain()

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout with {peername}")
                    break
                except ConnectionResetError:
                    logger.warning(f"Client {peername} reset connection")
                    break
                except Exception as e:
                    logger.error(f"Error processing data from {peername}: {str(e)}")
                    break

        except Exception as e:
            logger.error(f"Unexpected error with {peername}: {str(e)}")
        finally:
            try:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=2.0)
            except Exception:
                pass
            logger.info(f"Connection closed: {peername}")

    async def run(self):
        server = await asyncio.start_server(
            self.handle_client,
            settings.TCP_HOST,
            settings.TCP_PORT
        )
        logger.info(f"Server running on {settings.TCP_HOST}:{settings.TCP_PORT}")

        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = GT06Server()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {str(e)}")