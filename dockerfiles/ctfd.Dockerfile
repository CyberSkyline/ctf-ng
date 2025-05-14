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
COPY ./conf/ctfd/start_devmode.sh /start_devmode.sh
COPY ./conf/ctfd/serve_debug.py ./serve_debug.py

ADD ./backend/ctfd/plugin /opt/CTFd/CTFd/plugins/placeholder
ADD ./backend/ctfd/entrypoint.html /opt/CTFd/CTFd/themes/core/templates/entrypoint.html

USER 1001
