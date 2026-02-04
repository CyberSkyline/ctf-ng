# Build stage - install dependencies
FROM python:3.12-bookworm AS builder

WORKDIR /opt/CTFd

# Install build dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  build-essential \
  libffi-dev \
  libssl-dev \
  git
RUN rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY ./external/CTFd/requirements.txt /opt/CTFd/requirements.txt

# Install base Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy full application for plugin dependencies
COPY ./external/CTFd /opt/CTFd

# Install plugin dependencies
RUN for d in CTFd/plugins/*; do \
  if [ -f "$d/requirements.txt" ]; then \
  pip install --no-cache-dir -r "$d/requirements.txt"; \
  fi; \
  done

# Copy and install CTF-ng plugin dependencies
COPY ./backend/ng/requirements.txt /opt/ng-requirements.txt
RUN pip install --no-cache-dir -r /opt/ng-requirements.txt

# Runtime stage - minimal runtime environment
FROM python:3.12-slim-bookworm

WORKDIR /opt/CTFd

# Install only runtime dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libffi8 \
  libssl3 \
  procps \
  net-tools \
  curl \
  supervisor
RUN rm -rf /var/lib/apt/lists/*

# Create ctfd user
RUN useradd \
  --no-log-init \
  --shell /bin/bash \
  -u 1001 \
  ctfd

RUN mkdir -p /var/log/CTFd /var/uploads

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=1001:1001 ./external/CTFd /opt/CTFd

# Copy plugin and templates
ADD --chown=1001:1001 ./backend/ng/ /opt/CTFd/CTFd/plugins/ng
COPY --chown=1001:1001 ./backend/views/* /opt/CTFd/CTFd/themes/core/templates/

# CTFd's .flaskenv is only for development mode. We are removing it and using our own env variables
RUN rm -f /opt/CTFd/.flaskenv

# Set up configurations and entrypoint
COPY ./conf/ctfd/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./conf/ctfd/config.ini /opt/CTFd/CTFd/config.ini
COPY ./conf/ctfd/entrypoint.sh /opt/CTFd/entrypoint.sh
COPY ./conf/ctfd/serve_debug.py /opt/CTFd/serve_debug.py
COPY ./conf/ctfd/init_patch /opt/CTFd/init_patch

RUN chown -R 1001:1001 /var/log/CTFd /var/uploads /opt/CTFd
RUN chmod +x /opt/CTFd/docker-entrypoint.sh /opt/CTFd/entrypoint.sh

ENV PATH="/opt/venv/bin:$PATH"

USER 1001
