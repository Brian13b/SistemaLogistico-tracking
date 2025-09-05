# Imagen de Python 3.13 Slim
FROM python:3.13-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto TCP
EXPOSE 5023

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]