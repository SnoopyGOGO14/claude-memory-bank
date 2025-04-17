FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Make scripts executable
RUN chmod +x *.py

# Expose port for web interface if needed
EXPOSE 8050

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command: run the example agent
CMD ["python", "agent_example.py", "--config"] 