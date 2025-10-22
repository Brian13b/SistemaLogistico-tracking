# Imagen de Python 3.11 Slim
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto TCP
EXPOSE 5023

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]