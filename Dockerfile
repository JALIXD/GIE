FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN ls -l /app/staticfiles/

EXPOSE 8000

CMD ["gunicorn", "gie_project.wsgi:application", "--bind", "0.0.0.0:8000"]
