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

    async def handle_client(self, reader, writer):
        peername = writer.get_extra_info('peername')
        logger.info(f"🟢 NUEVA CONEXIÓN: {peername}")

        try:
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=120.0)
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Timeout esperando datos de {peername}")
                    break

                if not data:
                    logger.info(f"🔴 Cliente {peername} desconectado (Socket cerrado)")
                    break

                # 1. LOG DEL HEX CRUDO
                hex_data = data.hex().upper()
                logger.debug(f"📥 RECIBIDO [{len(data)} bytes]: {hex_data}")

                # Validación básica de cabecera GT06 (0x78 0x78)
                if len(data) < 5 or data[0] != 0x78 or data[1] != 0x78:
                    logger.error(f"⚠️ Paquete basura o protocolo desconocido: {hex_data}")
                    continue

                try:
                    protocol = data[3]
                    device_id = data[4:12].hex() 
                    
                    # LOG DEL PROTOCOLO DETECTADO
                    proto_name = {0x01: "LOGIN", 0x12: "LBS", 0x13: "HEARTBEAT", 0x22: "GPS"}.get(protocol, f"UNKNOWN-{protocol:02X}")
                    logger.info(f"🔍 Protocolo: {proto_name} | Device: {device_id}")

                    # --- Lógica de Procesamiento ---

                    # A. PAQUETE DE LOGIN (0x01)
                    if protocol == 0x01:
                        packet = self.parser.parse_login(data)
                        logger.info(f"✅ Login OK | ID: {packet['device_id']}")
                        
                        # Responder ACK
                        serial = struct.unpack('>H', data[-6:-4])[0]
                        ack = self.parser.create_ack(serial)
                        writer.write(ack)
                        await writer.drain()
                        logger.debug(f"📤 ENVIADO ACK LOGIN: {ack.hex().upper()}")

                    # B. PAQUETE DE GPS (0x22, 0x12, etc)
                    elif protocol == 0x22: 
                        try:
                            packet = self.parser.parse_gps(data)
                            logger.info(f"📍 GPS DATOS | Lat: {packet['lat']}, Lng: {packet['lng']}, Speed: {packet['speed']}")
                            
                            # Enviar al Backend
                            success = await send_to_backend(packet)
                            if success:
                                logger.info("🚀 Datos enviados al Backend correctamente")
                            else:
                                logger.error("❌ Fallo al enviar al Backend")

                        except ValueError as ve:
                            logger.error(f"❌ Error parseando GPS: {ve}")

                        # Algunos trackers piden ACK para GPS, otros no. 
                        # Si tu tracker repite el mensaje, descomenta esto:
                        # serial = struct.unpack('>H', data[-6:-4])[0]
                        # ack = self.parser.create_ack(serial)
                        # writer.write(ack)
                        # await writer.drain()

                    # C. HEARTBEAT (0x13) - Importante responder para mantener conexión
                    elif protocol == 0x13:
                        logger.info("💓 Heartbeat recibido")
                        serial = struct.unpack('>H', data[-6:-4])[0]
                        ack = self.parser.create_ack(serial)
                        writer.write(ack)
                        await writer.drain()
                        logger.debug(f"📤 ENVIADO ACK HEARTBEAT: {ack.hex().upper()}")

                    else:
                        logger.warning(f"⚠️ Protocolo no manejado: {hex(protocol)}")

                except Exception as e:
                    logger.exception(f"💥 Error procesando paquete: {str(e)}")
                    # Importante: No romper el loop por un paquete mal formado
                    continue

        except Exception as e:
            logger.error(f"💥 Error crítico en conexión con {peername}: {str(e)}")
        finally:
            writer.close()
            logger.info(f"🔒 Conexión cerrada: {peername}")

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