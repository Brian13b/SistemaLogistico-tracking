# 🛰️ Módulo de Tracking GPS en Tiempo Real

El corazón del monitoreo del **Sistema Logístico**. Este módulo híbrido combina un servidor de sockets de alto rendimiento para hardware IoT con una API REST para el consumo de datos.

---

## 🌟 Funcionalidades Principales
- **Servidor TCP Asíncrono:** Escucha activa de tramas de datos provenientes de dispositivos GPS.
- **Decodificación de Tramas:** Parsea cadenas de datos (latitud, longitud, velocidad, motor on/off).
- **API de Consulta:** Endpoints para obtener la última ubicación conocida o historial de recorridos.
- **Vinculación:** Asocia identificadores de hardware (IMEI) con vehículos del sistema.

---

## 📚 Flujo de Datos
1.  **Dispositivo GPS:** Envía trama string vía TCP -> `Host:Puerto`.
2.  **Servidor TCP:** - Acepta la conexión.
    - Parsea la trama.
    - Inserta el registro en la base de datos `tracking_db`.
3.  **Frontend:** Consulta `GET /ubicaciones/{id}` a través del Gateway.
4.  **Mapa:** Renderiza el marcador en tiempo real usando Leaflet.

---

## 🛡️ Stack Tecnológico
- **Servidor Sockets:** Python `asyncio`.
- **API:** FastAPI.
- **Base de Datos:** PostgreSQL.
- **Protocolo:** TCP (Receptor) / HTTP (Consulta).

---

## 🌱 Futuras Actualizaciones
- [ ] **WebSockets:** Reemplazar el *polling* del frontend por un canal de WebSockets para movimiento fluido en vivo.
- [ ] **Geocercas (Geofencing):** Alertas si un vehículo sale de una zona delimitada.
- [ ] **Reproducción de Historial:** "Player" para ver la animación de un recorrido pasado.
- [ ] **Soporte Multi-protocolo:** Adaptadores para diferentes marcas de GPS (Teltonika, Ruptela, etc.).

---

## 👤 Autor
**Brian Battauz** - [GitHub](https://github.com/Brian13b)