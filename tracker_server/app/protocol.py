import struct
import logging
from datetime import datetime

logger = logging.getLogger("ProtocolParser")

class GT06ProtocolParser:
    
    @staticmethod
    def calculate_crc(data: bytes) -> bytes:
        """Calcula CRC-ITU (X.25) standard para GT06"""
        crc = 0xB704 
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
        
        device_id = data[4:12].hex()
        return {
            'type': 'login',
            'device_id': device_id
        }

    @staticmethod
    def parse_gps(data: bytes) -> dict:
        if len(data) < 30:
            raise ValueError(f"Paquete GPS muy corto ({len(data)} bytes)")

        try:
            year = 2000 + data[4]
            month = data[5]
            day = data[6]
            hour = data[7]
            minute = data[8]
            second = data[9]
            
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
            
            course_status = struct.unpack('>H', data[20:22])[0]
            course = course_status & 0x03FF # 10 bits para el curso
            
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
        Crea paquete de confirmación (ACK) para GT06.
        Estructura: Start(2) | Len(1) | Protocol(1) | Serial(2) | CRC(2) | Stop(2)
        """

        body = struct.pack('>BBH', 0x05, 0x01, serial_number)
        
        crc = GT06ProtocolParser.calculate_crc(body)
        
        return b'\x78\x78' + body + crc + b'\x0D\x0A'