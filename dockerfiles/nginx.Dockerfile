FROM nginx:1.29.3

RUN apt-get update \
  && apt-get install -y --no-install-recommends awscli \
  && rm -rf /var/lib/apt/lists/*
