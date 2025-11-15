# Use an official lightweight Python image
FROM python:3.11-slim

# Install system dependencies
# libpcap-dev is CRITICAL for Scapy to build
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y libpcap-dev
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# The command to run the application
CMD ["python", "main.py"]