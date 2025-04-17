FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Expose API port
EXPOSE 5000

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]
