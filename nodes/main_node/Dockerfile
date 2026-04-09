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

FROM ubuntu:22.04

LABEL authors="Pedro Guillem-Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>"
LABEL vendor="Structural Bioinformatics - Pisabarro Group - TU Dresden"
LABEL version="1.0"
LABEL description="DYME: Dynamic Mutagenesis Engine - Main Node"
LABEL license="GPLv3"

# Default UID/GID, overridden by install.sh
ARG DYME_UID=1000
ARG DYME_GID=1000
ARG MODELLER_LICENSE

ENV DEBIAN_FRONTEND=noninteractive
ENV KEY_MODELLER=${MODELLER_LICENSE}
ENV TZ=Etc/UTC

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

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        jq \
        numactl \
        procps \
        wget \
        tzdata; \
    rm -rf /var/lib/apt/lists/*

# Create mongodb group/user using host UID/GID
# -o allows a non-unique GID, which you need when the host GID already exists in the image
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

# MongoDB 8.0 repo for Ubuntu 22.04 (Jammy)
ARG MONGO_MAJOR=8.0

RUN set -eux; \
    curl -fsSL "https://www.mongodb.org/static/pgp/server-${MONGO_MAJOR}.asc" \
        | gpg --dearmor -o "/usr/share/keyrings/mongodb-server-${MONGO_MAJOR}.gpg"; \
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-${MONGO_MAJOR}.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/${MONGO_MAJOR} multiverse" \
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

RUN export KEY_MODELLER=${MODELLER_LICENSE} && \
    conda install -y -n dyme_main salilab::modeller && \
    conda clean --all -y

#########################################################################################################################
# STEP 4 - WEB SERVER SETUP
#########################################################################################################################

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        apache2 \
        libapache2-mod-php \
        libapache2-mod-wsgi-py3; \
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
RUN chown -R www-data:www-data /dyme_root/projects
RUN chmod -R 775 /dyme_root/projects

WORKDIR /
#RUN a2enmod wsgi
RUN a2enmod rewrite

#########################################################################################################################
# STEP 5 - ENTRYPOINT
#########################################################################################################################

COPY ./nodes/main_node/dyme-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/dyme-entrypoint.sh

ENV PATH=/usr/local/bin:/dyme_env/anaconda/envs/dyme_main/bin:${PATH}

ENTRYPOINT ["/usr/local/bin/dyme-entrypoint.sh"]

EXPOSE 27017
EXPOSE 80
