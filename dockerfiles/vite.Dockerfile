FROM node:24

USER root

RUN apt-get update
RUN npm install -g vite

WORKDIR /app/frontend

CMD [ "/bin/bash", "-c", "vite" ]
