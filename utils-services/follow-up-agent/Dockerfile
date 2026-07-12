# Use an official lightweight Python image
FROM python:3.11-slim as build-stage

# Install build dependencies
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Use the same base image for the final stage
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
COPY --from=build-stage /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build-stage /usr/local/bin /usr/local/bin

# Copy the rest of the application's source code into the container
COPY . .

# Expose the port that the FastAPI app runs on
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# The default port for uvicorn is 8000, which matches our docker-compose.yaml setup.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
