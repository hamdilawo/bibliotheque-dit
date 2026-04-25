# ── Dockerfile — Frontend React (multi-stage) ─────────────
# Stage 1 : build React
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json ./
RUN npm install --silent

COPY . .
RUN npm run build

# Stage 2 : serveur nginx léger
FROM nginx:alpine AS runtime

# Copier le build React
COPY --from=builder /app/build /usr/share/nginx/html

# Configuration nginx pour React Router (SPA)
RUN echo 'server { \
    listen 3000; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
