# Use a lightweight Python base image compatible with AMD64 architecture
# This ensures a small image size and CPU-only execution.
FROM python:3.9-slim-bullseye AS builder

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by PyMuPDF
# libglib2.0-0 is a common dependency for many Python libraries, including some used by PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# PyMuPDF is the primary library for PDF parsing
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ ./src/

# Command to run the application
# This command will be executed when the container starts.
# It calls the main.py script which handles all PDF processing.
CMD ["python", "src/main.py"]