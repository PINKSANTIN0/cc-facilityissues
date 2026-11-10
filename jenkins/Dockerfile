# ===============================================
# Dockerfile - Jenkins + Docker CLI + Python 3
# Facility Issue Reporting System
# Telkom University - Cloud Computing UTS
# ===============================================
# Image Jenkins resmi tidak punya docker, docker compose, maupun python3.
# Image ini menambahkan ketiganya supaya pipeline bisa menjalankan
# Syntax Check, Build Image, dan Deployment lewat docker.sock milik host.

FROM jenkins/jenkins:lts

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl python3 \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Tetap sebagai root agar bisa mengakses /var/run/docker.sock milik host
# dan menulis ke folder deploy yang di-bind-mount dari host.
