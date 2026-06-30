# user-service/Dockerfile
FROM python:3.11-slim
 
WORKDIR /app
 
# Install dependencies first (Docker layer cache optimisation)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
# Run as non-root user for security (NFR-4)
RUN adduser --disabled-password --gecos '' appuser
USER appuser
 
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "wsgi:app"]
