# Stage 1: Build stage
FROM python:3.11-slim as build-stage

# Install build dependencies
WORKDIR /tmp

# Install CPU-only torch first to avoid downloading large GPU binaries
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the installed packages from the build stage
COPY --from=build-stage /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build-stage /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Expose the port
EXPOSE 5005

# Define environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
