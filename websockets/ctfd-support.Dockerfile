FROM ctfd/ctfd:3.7.7

USER root

RUN apt-get update

RUN apt-get install -y \
  procps \
  net-tools \
  curl \
  supervisor

# Copy plugin and templates
ADD ./backend/ng/ /opt/CTFd/CTFd/plugins/ng
COPY ./backend/views/* /opt/CTFd/CTFd/themes/core/templates/

# Install plugin dependencies
RUN pip install --no-cache-dir -r /opt/CTFd/CTFd/plugins/ng/requirements.txt

# CTFd's .flaskenv is only for development mode. We are removing it and using our own env variables
RUN rm /opt/CTFd/.flaskenv

COPY ./websockets/supervisord-support.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./conf/ctfd/config.ini /opt/CTFd/CTFd/config.ini
COPY ./websockets/support-entrypoint.sh /opt/CTFd/support-entrypoint.sh
COPY ./websockets/serve_support.py /opt/CTFd/serve_support.py
RUN chmod +x /opt/CTFd/support-entrypoint.sh


USER 1001
