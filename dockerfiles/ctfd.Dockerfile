# FROM ctfd/ctfd:3.7.7

### 
FROM python:3.12-bookworm

WORKDIR /opt/CTFd

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  build-essential \
  libffi-dev \
  libssl-dev \
  git \
  libffi8 \
  libssl3 \
  && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=1001:1001 ./external/CTFd /opt/CTFd

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
  && for d in CTFd/plugins/*; do \
  if [ -f "$d/requirements.txt" ]; then \
  pip install --no-cache-dir -r "$d/requirements.txt"; \
  fi; \
  done \
  && useradd \
  --no-log-init \
  --shell /bin/bash \
  -u 1001 \
  ctfd \
  && mkdir -p /var/log/CTFd /var/uploads \
  && chown -R 1001:1001 /var/log/CTFd /var/uploads /opt/CTFd \
  && chmod +x /opt/CTFd/docker-entrypoint.sh

USER 1001
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]

### CTF-ng additions
USER root

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

# Set up configurations and entrypoint
COPY ./conf/ctfd/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./conf/ctfd/config.ini /opt/CTFd/CTFd/config.ini

COPY ./conf/ctfd/entrypoint.sh /opt/CTFd/entrypoint.sh
COPY ./conf/ctfd/serve_debug.py /opt/CTFd/serve_debug.py
COPY ./conf/ctfd/init_patch /opt/CTFd/init_patch
RUN chmod +x /opt/CTFd/entrypoint.sh

USER 1001
