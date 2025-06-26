FROM ctfd/ctfd:3.7.7

USER root

RUN apt-get update

RUN apt-get install -y \
  procps \
  net-tools \
  curl \
  supervisor

COPY ./conf/ctfd/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./conf/ctfd/entrypoint.sh /opt/CTFd/entrypoint.sh
COPY ./conf/ctfd/serve_debug.py /opt/CTFd/serve_debug.py
COPY ./conf/ctfd/config.ini /opt/CTFd/CTFd/config.ini

ADD ./backend/ng/ /opt/CTFd/CTFd/plugins/ng
COPY ./backend/views/* /opt/CTFd/CTFd/themes/core/templates/

RUN chmod +x /opt/CTFd/entrypoint.sh

# CTFd's .flaskenv is only for development mode. We are removing it and using our own env variables
RUN rm /opt/CTFd/.flaskenv

USER 1001
