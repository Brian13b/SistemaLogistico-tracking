import asyncio
import logging
import struct
from datetime import datetime, timezone
from app.config import settings
from app.protocol import GT06ProtocolParser
from app.handlers import send_to_backend

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("TrackerServer")

class GT06Server:
    def __init__(self):
        self.parser = GT06ProtocolParser()
        self.sessions = {}

    async def handle_client(self, reader, writer):
        peername = writer.get_extra_info('peername')
        logger.info(f"🟢 NUEVA CONEXIÓN: {peername}")

        try:
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=300.0)
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Timeout con {peername}")
                    break

                if not data:
                    logger.info(f"🔴 Desconectado: {peername}")
                    break

                if len(data) < 5:
                    continue
                
                header = data[0:2]
                if header not in [b'\x78\x78', b'\x79\x79']:
                    logger.debug(f"⚠️ Header desconocido: {header.hex()}")
                    continue

                try:
                    protocol = 0
                    if header == b'\x78\x78':
                        protocol = data[3]
                    else:
                        protocol = data[4]

                    device_id = self.sessions.get(writer)

                    if protocol == 0x01:
                        packet = self.parser.parse_login(data)
                        device_id = packet['device_id']
                        self.sessions[writer] = device_id
                        
                        logger.info(f"✅ Login OK | ID: {device_id}")
                        
                        serial = struct.unpack('>H', data[-6:-4])[0]
                        ack = self.parser.create_ack(serial)
                        writer.write(ack)
                        await writer.drain()

                    elif protocol == 0x22: 
                        if not device_id:
                            logger.warning("⚠️ Datos GPS recibidos sin Login previo")
                            continue
                            
                        packet = self.parser.parse_gps(data)
                        packet['device_id'] = device_id
                        
                        logger.info(f"📍 GPS | ID: {device_id} | Lat: {packet['lat']}, Lng: {packet['lng']}")
                        
                        await send_to_backend(packet)

                    elif protocol == 0x13: 
                        logger.info(f"💓 Heartbeat | ID: {device_id or 'Desconocido'}")
                        serial = struct.unpack('>H', data[-6:-4])[0]
                        ack = self.parser.create_ack(serial)
                        writer.write(ack)
                        await writer.drain()
                    
                    elif protocol == 0x12:
                        logger.info(f"📡 LBS (Sin GPS) | ID: {device_id or 'Desconocido'}")
                        serial = struct.unpack('>H', data[-6:-4])[0]
                        ack = self.parser.create_ack(serial)
                        writer.write(ack)
                        await writer.drain()

                    elif protocol == 0x94 or header == b'\x79\x79':
                        logger.warning(f"🔔 ALARMA Recibida | ID: {device_id or 'Desconocido'}")
                        if len(data) > 6:
                            serial = struct.unpack('>H', data[-6:-4])[0]
                            ack = self.parser.create_ack(serial)
                            writer.write(ack)
                            await writer.drain()

                except Exception as e:
                    logger.error(f"💥 Error procesando paquete: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error general: {str(e)}")
        finally:
            if writer in self.sessions:
                del self.sessions[writer]
            writer.close()

    async def run(self):
        logger.info(f"🚀 Iniciando servidor TCP en {settings.TCP_HOST}:{settings.TCP_PORT}")
        server = await asyncio.start_server(
            self.handle_client,
            settings.TCP_HOST,
            settings.TCP_PORT
        )
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = GT06Server()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por usuario")
    except Exception as e:
        logger.error(f"💥 Fallo fatal del servidor: {str(e)}")