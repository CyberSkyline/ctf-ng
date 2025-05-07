FROM node:24

USER root

RUN apt-get update

RUN npm install -g vite

# ADD ./frontend/ /app/

WORKDIR /app

# RUN yarn install

CMD [ "/bin/bash", "-c", "vite" ]