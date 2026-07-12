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

# Copy the requirements file into the container at /app
COPY . .

# Expose the port that the application runs on
EXPOSE 5005

# Set environment variables
ENV PYTHONUNBUFFERED=1

# The command to run the application as specified in the docker-compose setup
CMD ["python", "app.py"]