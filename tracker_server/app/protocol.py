import struct
from datetime import datetime

class GT06ProtocolParser:
    @staticmethod
    def parse_login(data: bytes) -> dict:
        """Parsea paquete de login (protocolo 0x01)"""
        if len(data) < 14:
            raise ValueError("Paquete de login demasiado corto")
        
        return {
            'type': 'login',
            'device_id': data[4:12].decode('ascii', errors='ignore').strip(),
            'firmware': data[12:14].hex()
        }

    @staticmethod
    def parse_gps(data: bytes) -> dict:
        """Parsea paquete GPS (protocolo 0x22)"""
        if len(data) < 34:
            raise ValueError("Paquete GPS demasiado corto")

        try:
            # ID del dispositivo (8 bytes ASCII)
            device_id = data[4:12].decode('ascii', errors='ignore').strip()
            
            # Fecha y hora (6 bytes)
            year = 2000 + data[12]
            month = data[13]
            day = data[14]
            hour = data[15]
            minute = data[16]
            second = data[17]
            
            # Coordenadas (4 bytes cada una, big-endian, con signo)
            lat = struct.unpack('>i', data[18:22])[0] / 1800000.0
            lng = struct.unpack('>i', data[22:26])[0] / 1800000.0
            
            # Validar coordenadas
            lat = max(min(lat, 90.0), -90.0)
            lng = max(min(lng, 180.0), -180.0)
            
            # Velocidad y rumbo
            speed = data[26]
            course = struct.unpack('>H', data[27:29])[0] % 360  # Normalizado 0-359
            
            # Flags y precisión
            flags = data[29]
            accuracy = 3 if flags & 0x80 else 15  # Alta precisión si bit 7 está activo
            
            # Altitud (2 bytes, en decímetros)
            altitude = struct.unpack('>H', data[30:32])[0] / 10.0  # Convertir a metros
            
            return {
                'type': 'gps',
                'device_id': device_id,
                'lat': round(lat, 6),
                'lng': round(lng, 6),
                'speed': min(speed, 255),  # Asegurar máximo 255 km/h
                'course': course,
                'altitude': round(altitude, 1),
                'accuracy': accuracy,
                'timestamp': datetime(
                    year, month, day, hour, minute, second
                ).isoformat() + "Z"
            }
        except Exception as e:
            raise ValueError(f"Error parsing GPS data: {str(e)}")

    @staticmethod
    def create_ack(device_id: str, packet_number: int) -> bytes:
        """Crea paquete de confirmación (ACK)"""
        return (
            bytes.fromhex("78780501") + 
            device_id.encode('ascii').ljust(8, b'\x00')[:8] + 
            bytes([packet_number]) + 
            bytes.fromhex("000D0A")
        )