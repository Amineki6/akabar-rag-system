# Use the same base Python image for consistency
FROM python:3.11-slim

WORKDIR /app

# Copy data files and scripts
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# This container will run all three loading scripts in sequence
# It waits for Redis to be available before running.
CMD ["sh", "-c", "python load_locations.py && python load_manifest.py && python load_music.py"]

