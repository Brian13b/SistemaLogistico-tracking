# Imagen de Python 3.11 Slim
FROM python:3.11-slim

# --- MEJORA: Variables para logs en tiempo real ---
# Evita archivos .pyc y fuerza la salida de logs sin buffer (vital para ver errores en la nube)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python (Esto está perfecto)
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto TCP (Asegúrate que main.py escuche en este puerto)
EXPOSE 5023

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]