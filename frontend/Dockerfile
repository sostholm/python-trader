FROM nginx:latest

COPY /build/ /app/
COPY nginx.conf /etc/nginx/nginx.conf

CMD ["watch", "--interval 2", "--errexit" "nginx", "-g", "daemon off;"]