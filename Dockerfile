FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
# RUN python manage.py migrate --noinput  # ← Solo si estás seguro

EXPOSE 8000

CMD ["gunicorn", "gie_project.wsgi:application", "--bind", "0.0.0.0:8000"]
