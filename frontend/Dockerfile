# Usa nginx para servir archivos estáticos
FROM nginx:alpine

# Copia los archivos estáticos (la carpeta public) al directorio de nginx
COPY public /usr/share/nginx/html

# Expone el puerto 80
EXPOSE 80

# Nginx se ejecuta en primer plano
CMD ["nginx", "-g", "daemon off;"]
