# ---- Stage 1: Build ----
# This stage installs dependencies and builds the static files for production.
FROM node:20-alpine AS build-stage

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker layer caching.
# This step will only be re-run if these files change.
COPY package*.json ./
RUN npm config set fetch-retries 5 \
    && npm config set fetch-retry-mintimeout 20000 \
    && npm config set fetch-retry-maxtimeout 120000 \
    && npm install

# Copy the rest of the application's source code
COPY . .

# --- NEW LINES START ---
# Receive the build argument passed from docker-compose.
ARG VITE_MAPBOX_ACCESS_TOKEN
# Set the ARG as an environment variable so the 'npm run build' script can access it.
ENV VITE_MAPBOX_ACCESS_TOKEN=$VITE_MAPBOX_ACCESS_TOKEN
# --- NEW LINES END ---

# Run the build script defined in package.json
RUN npm run build


# ---- Stage 2: Serve ----
# This stage takes the built files and serves them with a lightweight web server.
FROM nginx:stable-alpine AS production-stage

# --- FIX ---
# Modern JavaScript tools (like Vite) often output to a 'dist' folder, not 'build'.
# This line is changed to copy from the correct output directory.
COPY --from=build-stage /app/dist /usr/share/nginx/html

# If you have a custom nginx configuration, you can copy it here
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to the outside world
EXPOSE 80

# The default NGINX command will start the server automatically
CMD ["nginx", "-g", "daemon off;"]
