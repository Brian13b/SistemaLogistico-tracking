import struct
import logging
from datetime import datetime

logger = logging.getLogger("ProtocolParser")

class GT06ProtocolParser:
    
    @staticmethod
    def calculate_crc(data: bytes) -> bytes:
        """Calcula CRC-ITU (X.25) standard para GT06"""
        crc = 0xB704 # Valor semilla común GT06 (A veces es 0xFFFF, probar si falla)
        # Implementación simple de CRC-ITU
        crc = 0xFFFF 
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
            crc &= 0xFFFF
        return struct.pack('>H', crc)

    @staticmethod
    def parse_login(data: bytes) -> dict:
        if len(data) < 14:
            raise ValueError("Paquete login muy corto")
        
        # Usamos HEX para el ID, es más seguro que ASCII
        device_id = data[4:12].hex()
        return {
            'type': 'login',
            'device_id': device_id
        }

    @staticmethod
    def parse_gps(data: bytes) -> dict:
        # Validación de longitud mínima para paquete 0x22
        if len(data) < 30:
            raise ValueError(f"Paquete GPS muy corto ({len(data)} bytes)")

        try:
            # 1. Device ID (Bytes 4-12 no siempre están en paquetes GPS cortos, 
            # pero asumimos estructura standard extendida o usamos el ID de la conexión)
            # NOTA: En muchos protocolos GT06, el paquete GPS NO trae el ID. 
            # El ID se asocia al socket en el Login. 
            # Si tu tracker lo manda, genial. Si no, tendrás datos raros aquí.
            
            # Timestamp
            year = 2000 + data[4]
            month = data[5]
            day = data[6]
            hour = data[7]
            minute = data[8]
            second = data[9]
            
            # Coordenadas GT06: (Grados*60 + Minutos) * 30000
            # Info satelites (1 byte) -> data[10]
            
            raw_lat = struct.unpack('>i', data[11:15])[0]
            raw_lng = struct.unpack('>i', data[15:19])[0]
            
            def convert_coord(raw):
                val = raw / 30000.0
                deg = int(val / 60)
                mins = val % 60
                return deg + (mins / 60)

            lat = convert_coord(raw_lat)
            lng = convert_coord(raw_lng)
            
            speed = data[19]
            
            # Flags y Course (2 bytes: data[20], data[21])
            course_status = struct.unpack('>H', data[20:22])[0]
            course = course_status & 0x03FF # 10 bits para el curso
            
            # Ajuste lat/lng según hemisferio (Flags en course_status)
            # Esto varía según sub-versión de GT06, pero lo estándar:
            # Bit 10: 0=S, 1=N ? A veces viene directo en el signo del entero.
            # En GT06 puro, las coordenadas suelen ser siempre positivas y los flags definen signo.
            
            # Log de valores crudos para debuggeo fino
            logger.debug(f"Raw Lat: {raw_lat} -> {lat}, Raw Lng: {raw_lng} -> {lng}")

            return {
                'lat': round(lat, 6),
                'lng': round(lng, 6),
                'speed': speed,
                'course': course,
                'timestamp': datetime(year, month, day, hour, minute, second).isoformat()
            }
        except Exception as e:
            logger.error(f"Error parseando bytes GPS: {data.hex()}")
            raise e

    @staticmethod
    def create_ack(serial_number: int) -> bytes:
        """
        Crea respuesta generica.
        Format: Start(2) | Len(1) | Protocol(1) | Serial(2) | CRC(2) | Stop(2)
        """
        # Protocolo respuesta suele ser el mismo 0x01 o 0x05 genérico
        # Construimos el cuerpo para el CRC
        # Len = 5 (1 byte proto + 2 bytes serial + 2 bytes CRC error check?? No, CRC va al final)
        
        # Body: [Protocol_Resp] [Serial]
        # Para Login ACK, suele ser Protocolo 0x01
        body = b'\x05\x01' + struct.unpack('>2B', struct.pack('>H', serial_number)) # Hacky way to get bytes
        # Mejor:
        body = bytes([0x05, 0x01]) + struct.pack('>H', serial_number)
        
        crc = GT06ProtocolParser.calculate_crc(body)
        return b'\x78\x78' + body + crc + b'\x0D\x0A'