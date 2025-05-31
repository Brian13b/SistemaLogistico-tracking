import struct
from datetime import datetime

class GT06ProtocolParser:
    @staticmethod
    def parse_login(data: bytes) -> dict:
        return {
            'type': 'login',
            'device_id': data[4:12].hex(),
            'firmware': data[12:14].hex()
        }

    @staticmethod
    def parse_gps(data: bytes) -> dict:
        try:
            # Extraer componentes básicos
            device_id = data[4:8].hex()
            
            # Extraer y validar fecha/hora
            year = 2000 + data[8]
            month = min(max(data[9], 1), 12)
            day = min(max(data[10], 1), 31)
            hour = min(max(data[11], 0), 23)
            minute = min(max(data[12], 0), 59)
            second = min(max(data[13], 0), 59)
            
            # Extraer y convertir coordenadas
            raw_lat = struct.unpack('>i', data[14:18])[0]
            raw_lng = struct.unpack('>i', data[18:22])[0]
            lat = max(min(raw_lat / 1800000.0, 90.0), -90.0)
            lng = max(min(raw_lng / 1800000.0, 180.0), -180.0)
            
            # Extraer otros campos
            speed = data[22]
            course = struct.unpack('>H', data[23:25])[0] % 360  # Normalizar a 0-359
            flags = data[25]
            
            # Determinar altitud y precisión basado en flags
            altitude = 0  # Valor por defecto
            accuracy = 5 if flags & 0x80 else 20  # Ejemplo: bit 7 indica alta precisión
            
            return {
                'type': 'gps',
                'device_id': device_id,
                'lat': lat,
                'lng': lng,
                'speed': speed,
                'course': course,
                'altitude': altitude,
                'accuracy': accuracy,
                'timestamp': f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"
            }
        except Exception as e:
            raise ValueError(f"Error parsing GPS data: {str(e)}")

    @staticmethod
    def create_ack(device_id: str, packet_number: int) -> bytes:
        return bytes.fromhex(f"78780501{device_id}{packet_number:02x}00000d0a")