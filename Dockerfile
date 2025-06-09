FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias y archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Expone el puerto 8000
EXPOSE 8000

# Comando de producción
CMD ["gunicorn", "gie_project.wsgi:application", "--bind", "0.0.0.0:8000"]
