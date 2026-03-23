#"""
#DYME - Dynamic Mutagenesis Engine v0.1

#File:           Dockerfile
#Description:    Recipe to build the DYME docker container

# DyME works exclusively on X86_64 hardware. Especially the MD node.

#Author:     
#Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
#Structural Bioinformatics Laboratory 
#BIOTEC - Pisabarro Group
#Technische Universität Dresden
#June 2024

#Licensing:
# This software is free to use under the GPLv3 license, under the following considerations:

# - You may install and use DyME academically under the terms of the GPLv3 license.
# - Commercial usage is not allowed. If you use DyME for profit, you need to get a license.
# - Cite this work if you used it for your research.
# - You must be familiar with the licensing of all dependencies, particularly Anaconda and Modeller (Salilab).
# - You are not allowed to distribute this tool to third parties, or use/embed its code in third party tools for profit.
#
#   IMPORTANT!
# - Host a public web server using this software is not autorized (and you wouldn't want to).
#   DyME is meant to run in local networks where security is not a concern. It was designed to do science, 
#   not to comply with internet security standards.
###
FROM ubuntu:20.04

LABEL authors="Pedro Guillem-Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>"
LABEL vendor="Structural Bioinformatics - Pisabarro Group - TU Dresden"
LABEL version="1.0"
LABEL description="DYME: Dynamic Mutagenesis Engine - Main Node"
LABEL license="GPLv3"

# Default UID/GID, overridden by install.sh
ARG DYME_UID=1000
ARG DYME_GID=1000

ENV DEBIAN_FRONTEND=noninteractive

#########################################################################################################################
# STEP 1 - CREATE OUTPUT DIRECTORY FOR ASSETS & TRAJECTORIES
#########################################################################################################################

RUN set -eux; \
    mkdir -p /dyme_base; \
    mkdir -p /dyme_root/projects; \
    mkdir -p /dyme_root/database/mongodb; \
    mkdir -p /dyme_root/logs; \
    mkdir -p /docker-entrypoint-initdb.d; \
    mkdir -p /data/db; \
    mkdir -p /data/configdb

VOLUME /dyme_root

#########################################################################################################################
# STEP 2 - INSTALL BASE PACKAGES + MONGODB
#########################################################################################################################

# Create mongodb user using host UID/GID.
# Important: do not create the group if the GID already exists.
RUN set -eux; \
    if ! getent group mongodb >/dev/null; then \
        groupadd -g "${DYME_GID}" -o mongodb; \
    fi; \
    if ! id -u mongodb >/dev/null 2>&1; then \
        useradd \
            --uid "${DYME_UID}" \
            --gid mongodb \
            --home-dir /dyme_root/database/mongodb \
            --create-home \
            --shell /bin/bash \
            mongodb; \
    fi; \
    mkdir -p /dyme_root/database/mongodb /data/db /data/configdb; \
    chown -R "${DYME_UID}:${DYME_GID}" /dyme_root/database/mongodb /data/db /data/configdb

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        jq \
        numactl \
        procps \
        wget; \
    rm -rf /var/lib/apt/lists/*

# gosu for privilege drop
ENV GOSU_VERSION=1.17
# js-yaml for parsing mongod YAML config
ENV JSYAML_VERSION=3.13.1

RUN set -eux; \
    savedAptMark="$(apt-mark showmanual)"; \
    dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-${dpkgArch}"; \
    wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-${dpkgArch}.asc"; \
    export GNUPGHOME="$(mktemp -d)"; \
    gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
    gpgconf --kill all; \
    rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
    chmod +x /usr/local/bin/gosu; \
    gosu --version; \
    gosu nobody true; \
    mkdir -p /opt/js-yaml; \
    wget -O /opt/js-yaml/js-yaml.js "https://github.com/nodeca/js-yaml/raw/${JSYAML_VERSION}/dist/js-yaml.js"; \
    wget -O /opt/js-yaml/package.json "https://github.com/nodeca/js-yaml/raw/${JSYAML_VERSION}/package.json"; \
    ln -s /opt/js-yaml/js-yaml.js /js-yaml.js; \
    apt-mark auto '.*' > /dev/null; \
    apt-mark manual $savedAptMark > /dev/null; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

# MongoDB 8.0 repo, let apt choose latest available stable release in that branch
ARG MONGO_MAJOR=8.0

RUN set -eux; \
    curl -fsSL "https://www.mongodb.org/static/pgp/server-${MONGO_MAJOR}.asc" \
        | gpg --dearmor -o "/usr/share/keyrings/mongodb-server-${MONGO_MAJOR}.gpg"; \
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-${MONGO_MAJOR}.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/${MONGO_MAJOR} multiverse" \
        > "/etc/apt/sources.list.d/mongodb-org-${MONGO_MAJOR}.list"; \
    apt-get update; \
    apt-get install -y --no-install-recommends mongodb-org; \
    rm -rf /var/lib/apt/lists/*; \
    rm -rf /var/lib/mongodb; \
    mv /etc/mongod.conf /etc/mongod.conf.orig

COPY ./nodes/main_node/mongod.conf /etc/mongod.conf

#########################################################################################################################
# STEP 3 - DYME CONDA ENVIRONMENT
#########################################################################################################################

COPY ./nodes/main_node/dyme-env.yml /dyme-env.yml

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

ENV CONDA_DIR=/dyme_env/anaconda
ENV PATH=${CONDA_DIR}/bin:${PATH}

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p "${CONDA_DIR}" && \
    rm -f /tmp/miniconda.sh

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

RUN conda install -y -n base conda-libmamba-solver && \
    conda config --set solver libmamba

RUN conda env create -f /dyme-env.yml && \
    conda clean --all -y

#########################################################################################################################
# STEP 4 - WEB SERVER SETUP
#########################################################################################################################

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        apache2 \
        libapache2-mod-php7.4 \
        libapache2-mod-wsgi; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

COPY ./nodes/main_node/wsgi.load /etc/apache2/mods-available/wsgi.load
COPY ./nodes/main_node/wsgi.conf /etc/apache2/mods-available/wsgi.conf
COPY ./nodes/main_node/dyme-api.conf /etc/apache2/sites-available/

RUN mkdir -p /usr/lib64/httpd/modules
RUN cp -R /dyme_env/anaconda/envs/dyme_main/lib/python3.11/site-packages/mod_wsgi/server/mod_wsgi-py311.cpython-311-x86_64-linux-gnu.so /usr/lib64/httpd/modules/

COPY ./frontend /dyme_base/frontend
COPY ./nodes/source/ /dyme_base/backend/dyme
COPY ./backend/dyme/api /dyme_base/backend/dyme/api

RUN chown -R www-data:www-data /dyme_base/frontend

WORKDIR /etc/apache2/sites-enabled/
RUN ln -s ../sites-available/dyme-api.conf dyme-api.conf
RUN rm -f ../sites-available/000-default.conf 000-default.conf
RUN ln -s /dyme_root/projects /dyme_base/frontend/img/projects

WORKDIR /
RUN a2enmod wsgi

#########################################################################################################################
# STEP 5 - ENTRYPOINT
#########################################################################################################################

COPY ./nodes/main_node/dyme-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/dyme-entrypoint.sh

ENV PATH=/usr/local/bin:/dyme_env/anaconda/envs/dyme_main/bin:${PATH}

ENTRYPOINT ["/usr/local/bin/dyme-entrypoint.sh"]

EXPOSE 27017
EXPOSE 80