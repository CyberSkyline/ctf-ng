FROM ctfd/ctfd:3.7.7

USER root

RUN apt-get update

RUN apt-get install -y \
  procps \
  net-tools \
  curl \
  supervisor

COPY ./conf/ctfd/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./conf/ctfd/start.sh /start.sh

USER 1001
