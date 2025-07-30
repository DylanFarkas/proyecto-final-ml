# Etapa 1: Build
FROM node:18-alpine AS builder
WORKDIR /app

# Copiar archivos del frontend
COPY . .

RUN npm install

# Aquí es donde Vite usa la variable
RUN npm run build

# Etapa 2: Servir con nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
