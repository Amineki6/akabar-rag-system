# Use an official Python runtime as a parent image
FROM python:3.11-slim as build-stage

# Install build dependencies
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Use the same base image for the final stage
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the installed packages from the build stage
COPY --from=build-stage /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build-stage /usr/local/bin /usr/local/bin

# Copy the current directory contents into the container at /app
COPY . .

# Make port 5006 available to the world outside this container
EXPOSE 5006

# Define environment variables
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["python", "app.py"]
