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

#Default UID/GID.. this gets overriden by install.sh
ARG DYME_UID=1000
ARG DYME_GID=1000
#########################################################################################################################
# STEP 1 - CREATE OUTPUT DIRECTORY FOR ASSETS & TRAJECTORIES 

#Create DYME work directories 
#This should have the same structure as the volume mapping to dyme_root
RUN set -eux; \
    mkdir -p /dyme_base \
	mkdir -p /dyme_root/projects \
	mkdir -p /dyme_root/database/mongodb \	
    mkdir -p /dyme_root/logs \
	mkdir -p /docker-entrypoint-initdb.d 

#Declare Volumes
VOLUME /dyme_root


#STEP 2 - Install MongoDB (https://github.com/docker-library/mongo/blob/master/5.0/Dockerfile)
###############################################################################################################################
# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN set -eux; \
	getent group "${DYME_GID}"; \
	if ! id -u mongodb >/dev/null 2>&1; then \
		useradd --uid "${DYME_UID}" --gid "${DYME_GID}" --home-dir /dyme_root/database/mongodb mongodb; \
	fi; \
	mkdir -p /dyme_root/database/mongodb /data/db /data/configdb; \
	chown -R "${DYME_UID}:${DYME_GID}" /dyme_root/database/mongodb /data/db /data/configdb


RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		ca-certificates \
		jq \
		numactl \
		procps \
	; \
	rm -rf /var/lib/apt/lists/*

# grab gosu for easy step-down from root (https://github.com/tianon/gosu/releases)
ENV GOSU_VERSION 1.17
# grab "js-yaml" for parsing mongod's YAML config files (https://github.com/nodeca/js-yaml/releases)
ENV JSYAML_VERSION 3.13.1

RUN set -eux; \
	\
	savedAptMark="$(apt-mark showmanual)"; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		gnupg \
		wget \
	; \
	rm -rf /var/lib/apt/lists/*; \
	\
# download/install gosu
	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
	wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
	wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
	gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
	gpgconf --kill all; \
	rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
	\
# download/install js-yaml
	mkdir -p /opt/js-yaml/; \
	wget -O /opt/js-yaml/js-yaml.js "https://github.com/nodeca/js-yaml/raw/${JSYAML_VERSION}/dist/js-yaml.js"; \
	wget -O /opt/js-yaml/package.json "https://github.com/nodeca/js-yaml/raw/${JSYAML_VERSION}/package.json"; \
	ln -s /opt/js-yaml/js-yaml.js /js-yaml.js; \
# TODO some sort of download verification here
	\
# download/install MongoDB PGP keys
	export GNUPGHOME="$(mktemp -d)"; \
	wget -O KEYS 'https://pgp.mongodb.com/server-5.0.asc'; \
	gpg --batch --import KEYS; \
	mkdir -p /etc/apt/keyrings; \
	gpg --batch --export --armor 'F5679A222C647C87527C2F8CB00A0BD1E2C63C11' > /etc/apt/keyrings/mongodb.asc; \
	gpgconf --kill all; \
	rm -rf "$GNUPGHOME" KEYS; \
	\
	apt-mark auto '.*' > /dev/null; \
	apt-mark manual $savedAptMark > /dev/null; \
	apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
	\
# smoke test
	chmod +x /usr/local/bin/gosu; \
	gosu --version; \
	gosu nobody true

#Download


# Options for MONGO_PACKAGE: mongodb-org OR mongodb-enterprise
# Options for MONGO_REPO: repo.mongodb.org OR repo.mongodb.com
# Example: docker build --build-arg MONGO_PACKAGE=mongodb-enterprise --build-arg MONGO_REPO=repo.mongodb.com .
ARG MONGO_PACKAGE=mongodb-org
ARG MONGO_REPO=repo.mongodb.org
ENV MONGO_PACKAGE=${MONGO_PACKAGE} MONGO_REPO=${MONGO_REPO}
ENV MONGO_MAJOR 5.0

RUN echo "deb [ signed-by=/etc/apt/keyrings/mongodb.asc ] http://$MONGO_REPO/apt/ubuntu focal/${MONGO_PACKAGE%-unstable}/$MONGO_MAJOR multiverse" | tee "/etc/apt/sources.list.d/${MONGO_PACKAGE%-unstable}.list"

# https://docs.mongodb.org/master/release-notes/5.0/
ENV MONGO_VERSION 5.0.26
# 03/20/2024, https://github.com/mongodb/mongo/tree/0b4f1ea980b5380a66425a90b414106a191365f4

RUN set -x \
# installing "mongodb" pulls in "tzdata" which prompts for input
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update \
	&& apt-get install -y \
		${MONGO_PACKAGE}=$MONGO_VERSION \
		${MONGO_PACKAGE}-server=$MONGO_VERSION \
		${MONGO_PACKAGE}-shell=$MONGO_VERSION \
		${MONGO_PACKAGE}-mongos=$MONGO_VERSION \
		${MONGO_PACKAGE}-tools=$MONGO_VERSION \
		curl gpg \
	&& rm -rf /var/lib/mongodb \
	&& mv /etc/mongod.conf /etc/mongod.conf.orig

#Declare /data/db as a persistent volume
COPY ./nodes/main_node/mongod.conf /etc/mongod.conf



#########################################################################################################################
# STEP 3 - DYME CONDA ENVIRONMENT
#WORKDIR /group/bioinfp_apps/anaconda/
COPY ./nodes/main_node/dyme-env.yml /dyme-env.yml

#Install Miniconda
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 
    
#Path to conda
#Create 3 main DYME work directories

ENV CONDA_DIR /dyme_env/anaconda

#Install Miniconda quietly
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /dyme_env/anaconda

#Make conda executable    
ENV PATH=$CONDA_DIR/bin:$PATH

#Comply with non-interactive ToS of anaconda (users agreed to the license)
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
 && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

#Keep things fast.. default solver sucks
RUN conda install -y -n base conda-libmamba-solver
RUN conda config --set solver libmamba
#Ok, now we can create the environment! 
RUN conda env create -f /dyme-env.yml
#The main node only uses few functions of openmm.app and PDB handling classes.
#cudatoolkit is a dependency of openmm, but we can safely uninstall (for space!)
#no dynamics will be running in this server
#RUN conda remove --force cudatoolkit 
RUN conda clean --all -y

#clean a bit
RUN rm -Rf ~/miniconda.sh



#########################################################################################################################
# STEP 4 - WEB SERVER SETUP (Apache2/PHP7/WSGI for Python API)
RUN apt-get update \
    && apt-get install -y apache2 \
    && apt-get install -y libapache2-mod-php7.4 \
	&& apt-get install -y libapache2-mod-wsgi \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#PEDRO - You must Setup the VirtualHost file with wsgi
COPY    ./nodes/main_node/wsgi.load /etc/apache2/mods-available/wsgi.load
COPY    ./nodes/main_node/wsgi.conf /etc/apache2/mods-available/wsgi.conf
COPY    ./nodes/main_node/dyme-api.conf /etc/apache2/sites-available/

#Copy the appropriate mod_wsgi shared library, so apache WSGI loads the same python version as conda
RUN     mkdir -p /usr/lib64/httpd/modules/
RUN     cp -R /dyme_env/anaconda/envs/dyme_main/lib/python3.11/site-packages/mod_wsgi/server/mod_wsgi-py311.cpython-311-x86_64-linux-gnu.so /usr/lib64/httpd/modules/

#Copy frontend/backend code
COPY ./frontend /dyme_base/frontend
COPY ./nodes/source/ /dyme_base/backend/dyme
COPY ./backend/dyme/api /dyme_base/backend/dyme/api

#Set the right ownership
RUN chown -R www-data /dyme_base/frontend
RUN chgrp -R www-data /dyme_base/frontend

#Activate Sites Enabled in Virtualhosts
WORKDIR /etc/apache2/sites-enabled/
RUN ln -s ../sites-available/dyme-api.conf dyme-api.conf
RUN rm -Rf ../sites-available/000-default.conf 000-default.conf
#Create path for web UI to access outputs
RUN ln -s /dyme_root/projects /dyme_base/frontend/img/projects

#Change workdir to root
WORKDIR /

#Activate Apache wsgi
RUN a2enmod wsgi

#########################################################################################################################
# STEP 6 - FINALIZE PORTS AND REDIRECTS

#Copy the service startup file to the container
COPY ./nodes/main_node/dyme-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/dyme-entrypoint.sh
#Add anaconda bins to path (enables executables of the API to run (leap etc))
ENV PATH=/usr/local/bin:/dyme_root/anaconda/envs/dyme_main/bin:$PATH

ENTRYPOINT ["/usr/local/bin/dyme-entrypoint.sh"]
#SHELL bash

# Expose MongoDB Database port and Web server
EXPOSE 27017
EXPOSE 80

#Run mongodb Database
#CMD ["mongod", "--bind_ip_all"]

# TO RUN AND MAP A LOCAL DIR TO A CONTAINER DIR 
# YOU HAVE TO MAP THE DIR WHERE THE MOLECULAR DYNAMICS WILL BE AND THE RAMDRIVE

#THis next line you can execute from a custom script, not here
#docker run -it --mount src="$(pwd)", target=/superfast/dyme/projects,type=bind --mount type=tmpfs,destination=/mnt/ramdisk/mutants, IMAGENAME