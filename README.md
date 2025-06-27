# 🛰️ Módulo de rastreo en tiempo real para el sistema de gestión de flotas.  

Este repositorio forma parte del ecosistema de **Sistema Logistico** y está dedicado al rastreo de vehículos en tiempo real. Incluye un servidor **TCP** que recibe datos directamente desde dispositivos **GPS tracker** instalados en los vehículos, y un backend construido con **FastAPI** que gestiona, almacena y expone esa información para el resto del sistema.

---

🌟 **¿Qué hace este módulo?**  
- Recibe datos de ubicación y estado de los vehículos en tiempo real mediante un servidor **TCP**.  
- Procesa y envía esa información al backend para su almacenamiento y análisis.  
- Expone una API para que el frontend pueda acceder a los datos y mostrarlos en mapas o reportes.

---

🔧 **Características principales**  
- 📡 **Servidor TCP** para recibir datos en tiempo real desde trackers GPS.  
- 🗺️ Gestión de datos de ubicación: latitud, longitud, velocidad, dirección, estado, kilómetros recorridos y más.  
- 🔄 Integración directa con el backend para guardar datos en la base de datos.  
- 🌐 API REST con FastAPI para consulta y visualización desde el frontend.

---

📚 **Flujo del sistema**  
1. 📶 Tracker GPS → se conecta al servidor TCP.  
2. 📡 El servidor recibe y procesa los datos del vehículo.  
3. 💾 El backend guarda esta información en la base de datos.  
4. 🌍 El frontend obtiene los datos desde la API para visualizarlos en el mapa y generar reportes.

---

🛡️ **Tecnologías Usadas**  
- 🖥️ Lenguaje: Python
- ⚡ Framework: FastAPI (API REST)
- 📡 Protocolo de comunicación: TCP socket server
- 🗄️ Base de datos: PostgreSQL 

---

🌱 **Futuras actualizaciones**  
- 🔔 Notificaciones automáticas ante eventos críticos o cambios de estado.  
- 📈 Mejora en el análisis histórico de recorridos.  
- 📲 Visualización móvil optimizada para tracking en campo.

---