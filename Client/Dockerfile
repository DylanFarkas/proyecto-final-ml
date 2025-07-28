# Etapa 1: Build
FROM node:18-alpine AS builder
WORKDIR /app

# --- Asegura que la variable ARG se define ---
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Copiar archivos del frontend
COPY . .

RUN npm install

# Aquí es donde Vite usa la variable
RUN npm run build

# Etapa 2: Servir con nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
