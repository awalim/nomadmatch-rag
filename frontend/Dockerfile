FROM node:18-alpine

WORKDIR /app

# Copiar package files
COPY package.json ./

# Instalar dependencias
RUN npm install --no-package-lock

# Crear directorio public si no existe
RUN mkdir -p public

# Copiar archivos de la aplicación
COPY public/ ./public/

EXPOSE 3000

# Comando para servir archivos estáticos
CMD ["npx", "live-server", "public", "--port=3000", "--host=0.0.0.0", "--no-browser", "--watch=public", "--entry-file=index.html"]
