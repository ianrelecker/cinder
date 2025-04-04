# Improved Dockerfile for MITRE Caldera
# This file uses a staged build with proper layer caching and optimization

# Stage 1: UI Build
FROM node:20-alpine AS ui-build
WORKDIR /usr/src/app/plugins/magma

# Copy only package files first to leverage Docker cache
COPY plugins/magma/package*.json ./
RUN npm ci

# Copy the rest of the UI files and build
COPY plugins/magma/ ./
RUN npm run build

# Stage 2: Python Dependencies
FROM python:3.11-slim AS python-deps
WORKDIR /usr/src/app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Runtime
FROM python:3.11-slim AS runtime

# Build arguments
ARG VARIANT=slim
ARG TZ="UTC"
ENV VARIANT=${VARIANT}
ENV TZ=${TZ}

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

WORKDIR /usr/src/app

# Install runtime dependencies
RUN apt-get update && \
    apt-get --no-install-recommends -y install \
    git \
    curl \
    unzip \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from the python-deps stage
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the UI build from the ui-build stage
COPY --from=ui-build /usr/src/app/plugins/magma/dist /usr/src/app/plugins/magma/dist

# Copy application code
COPY . .

# For offline atomic (conditional based on variant)
RUN if [ "$VARIANT" = "full" ] && [ ! -d "/usr/src/app/plugins/atomic/data/atomic-red-team" ]; then \
        git clone --depth 1 https://github.com/redcanaryco/atomic-red-team.git \
            /usr/src/app/plugins/atomic/data/atomic-red-team; \
    elif [ "$VARIANT" = "slim" ]; then \
        sed -i '/\- atomic/d' conf/default.yml; \
    fi

# For offline emu (conditional based on variant)
RUN if [ "$VARIANT" = "full" ] && [ ! -d "/usr/src/app/plugins/emu/data/adversary-emulation-plans" ]; then \
        git clone --depth 1 https://github.com/center-for-threat-informed-defense/adversary_emulation_library \
            /usr/src/app/plugins/emu/data/adversary-emulation-plans; \
    fi

# Download emu payloads
RUN if [ -d "/usr/src/app/plugins/emu" ]; then \
        cd /usr/src/app/plugins/emu && ./download_payloads.sh; \
    fi

# Remove .git directories to reduce image size
RUN find . -type d -name ".git" -exec rm -rf {} +

# Expose ports
# HTTP/HTTPS
EXPOSE 8888 8443
# TCP/UDP
EXPOSE 7010 7011/udp
# Websocket
EXPOSE 7012
# DNS
EXPOSE 8853
# SSH
EXPOSE 8022
# FTP
EXPOSE 2222

# Use SIGINT for graceful shutdown
STOPSIGNAL SIGINT

# Set entrypoint
ENTRYPOINT ["python3", "server.py"]
