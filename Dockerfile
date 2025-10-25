FROM python:3.11-slim

# Set timezone to Moscow
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory and set permissions
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Copy all files
COPY . .

# Verify that app directory exists
RUN ls -la /app/
RUN ls -la /app/app/

# Add current directory to Python path
ENV PYTHONPATH=/app

EXPOSE 8083

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"] 