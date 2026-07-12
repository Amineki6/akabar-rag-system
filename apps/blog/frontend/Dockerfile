FROM nginx:alpine

# Remove default Nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy your custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy your frontend source files
COPY ./src /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]