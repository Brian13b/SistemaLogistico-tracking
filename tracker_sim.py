import socket
import threading
import time
import logging
import math
from datetime import datetime, timezone
import random
import struct
import ssl

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dispositivos reales
DISPOSITIVOS = [
    {
        "imei": "36377367",
        "patente": "AA123CV"
    },
    {
        "imei": "31313131",
        "patente": "AB256FG"
    },
    {
        "imei": "38393939",
        "patente": "AG845FR"
    }
]

# Ruta Rosario -> Cordoba
RUTA = [(-32.716774, -60.727609), (-31.466840, -64.101087)]

def crear_paquete_login(imei: str) -> bytes:
    """Crea paquete de login con formato correcto"""
    device_id = imei[:8].ljust(8, '0')[:8]
    if len(device_id) != 8:
        raise ValueError("El imei debe tener al menos 8 caracteres")
    
    return (
        bytes.fromhex("7878") +         # Header
        bytes([0x11]) +                 # Length
        bytes([0x01]) +                 # Protocol
        device_id.encode('ascii') +     # Device ID
        bytes.fromhex("000000000000") + # Datos fijos
        bytes.fromhex("0D0A")           # End
    )

def crear_paquete_gps(imei: str, lat: float, lng: float, speed: float, course: float) -> bytes:
    """Crea paquete GPS con formato compatible"""
    now = datetime.now(timezone.utc)
    device_id = imei[:8].ljust(8, '0')[:8]
    
    # Convertir coordenadas
    lat_int = int(lat * 1000000)
    lng_int = int(lng * 1000000)
    
    # Construir paquete
    return (
        bytes.fromhex("7878") +
        bytes([0x22]) +                           # Length
        bytes([0x22]) +                           # Protocol
        device_id.encode('ascii') +               # Device ID
        bytes([now.year - 2000]) +                # Year
        bytes([now.month]) +                      # Month
        bytes([now.day]) +                        # Day
        bytes([now.hour]) +                       # Hour
        bytes([now.minute]) +                     # Minute
        bytes([now.second]) +                     # Second
        lat_int.to_bytes(4, 'big', signed=True) + # Latitude
        lng_int.to_bytes(4, 'big', signed=True) + # Longitude
        bytes([min(int(speed), 255)]) +           # Speed
        struct.pack('>H', int(course) % 360) +    # Course
        bytes([0x80]) +                           # Flags (alta precision)
        bytes([0, 0]) +                           # Altitude
        bytes([5]) +                              # Accuracy
        bytes.fromhex("0000") +                   # Checksum (simulado)
        bytes.fromhex("0D0A")                     # End
    )

def simular_vehiculo(imei: str, patente: str, host: str, port: int):
    """Simula un vehiculo enviando datos realistas"""
    
    try:
        # 1. Configuración SSL
        context = ssl.create_default_context()
        
        # OJO: Si te da error de certificado (SSL: CERTIFICATE_VERIFY_FAILED),
        # descomenta estas dos lineas para pruebas:
        # context.check_hostname = False
        # context.verify_mode = ssl.CERT_NONE

        # 2. Socket crudo
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 3. Envolver y Conectar
        with context.wrap_socket(raw_socket, server_hostname=host) as s:
            s.connect((host, port))
            
            # Enviar login
            login_pkt = crear_paquete_login(imei)
            s.sendall(login_pkt)
            logger.info(f"✅ {patente}: Conectado a la nube y Login enviado")
            
            # Inicializar posición
            lat, lng = RUTA[0]
            lat += random.uniform(-0.01, 0.01)
            lng += random.uniform(-0.01, 0.01)
            
            while True:
                last_lat, last_lng = lat, lng
                
                # Movimiento hacia el destino
                destino_lat, destino_lng = RUTA[1]
                lat += (destino_lat - lat) * random.uniform(0.0001, 0.001)
                lng += (destino_lng - lng) * random.uniform(0.0001, 0.001)
                
                # Cálculos
                distancia_recorrida_km = haversine(last_lng, last_lat, lng, lat)
                speed = min(90, (distancia_recorrida_km * 3600 / 10))
                course = math.degrees(math.atan2(lng - last_lng, lat - last_lat)) % 360
                
                # Enviar paquete GPS
                gps_pkt = crear_paquete_gps(imei, lat, lng, speed, course)
                s.sendall(gps_pkt)
                logger.info(f"📡 {patente}: Enviado -> Pos {lat:.4f},{lng:.4f} | Vel: {speed:.1f}")
                
                time.sleep(10)
                
    except Exception as e:
        logger.error(f"❌ Error con {patente}: {e}")
        # Pequeña pausa para no saturar la CPU si falla en bucle
        time.sleep(5)

def haversine(lon1, lat1, lon2, lat2):
    """Calcula la distancia en km entre dos puntos geográficos"""
    from math import radians, sin, cos, sqrt, asin
    
    # Convertir grados a radianes
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Diferencias
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    
    # Fórmula Haversine
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radio de la Tierra en km
    return c * r

if __name__ == "__main__":
    HOST_NUBE = "sistema-tracking-tcp.fly.dev" 
    PUERTO_NUBE = 443

    threads = []
    
    logger.info(f"🚀 Iniciando simulación hacia {HOST_NUBE}:{PUERTO_NUBE}")

    for dispositivo in DISPOSITIVOS:
        thread = threading.Thread(
            target=simular_vehiculo,
            args=(
                dispositivo["imei"],
                dispositivo["patente"],
                HOST_NUBE,    # <--- Usamos la IP de la nube
                PUERTO_NUBE   # <--- Puerto 5023
            ),
            daemon=True
        )
        thread.start()
        threads.append(thread)
        time.sleep(0.5) # Pequeña pausa para no saturar el inicio
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nDeteniendo simulaciones...")