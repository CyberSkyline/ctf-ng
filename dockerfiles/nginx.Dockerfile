FROM nginx:1.29.3

RUN apt-get update \
  && apt-get install -y --no-install-recommends awscli \
  && rm -rf /var/lib/apt/lists/*

COPY conf/nginx/ /opt/nginx/conf/
COPY conf/nginx/http.prod.conf /etc/nginx/nginx.conf
COPY frontend/dist/ /var/www/vite-build/
