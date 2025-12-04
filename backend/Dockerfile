FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5100

CMD ["gunicorn", "-w", "4", "--worker-class", "gevent", "--bind", "0.0.0.0:5100", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "120", "wsgi:app"]
