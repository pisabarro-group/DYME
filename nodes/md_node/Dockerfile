#"""
#DYME - Dynamic Mutagenesis Engine v0.1

#File:           Dockerfile
#Description:    Recipe to build the DYME docker container

# DyME works exclusively on X86_64 hardware. Specially the MD node.

# Author:     
# Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
# Structural Bioinformatics Laboratory 
# BIOTEC - Pisabarro Group
# Technische Universität Dresden
# June 2024

FROM nvidia/cuda:12.3.0-base-ubuntu22.04

LABEL authors="Pedro Guillem-Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>"
LABEL vendor="Structural Bioinformatics - Pisabarro Group - TU Dresden"
LABEL version="1.0"
LABEL description="DYME: Dynamic Mutagenesis Engine - Node Container"
LABEL license="GPLv3"

ARG MODELLER_LICENSE

ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV KEY_MODELLER=${MODELLER_LICENSE}

#########################################################################################################################
# STEP 1 - BASE PACKAGES AND DIRECTORY STRUCTURE
#########################################################################################################################

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        ca-certificates; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    mkdir -p /dyme_base; \
    mkdir -p /dyme_env; \
    mkdir -p /dyme_root/nodes/source; \
    mkdir -p /dyme_root/projects; \
    mkdir -p /dyme_root/logs; \
    mkdir -p /mnt/ramdrive; \
    mkdir -p /docker-entrypoint-initdb.d

VOLUME /dyme_root

#########################################################################################################################
# STEP 2 - CONDA ENVIRONMENT
#########################################################################################################################

COPY ./nodes/md_node/dyme_md.yml /dyme-md.yml
COPY ./nodes/md_node/constraints.txt /tmp/constraints.txt

ENV CONDA_DIR=/dyme_env/anaconda
ENV PATH=${CONDA_DIR}/bin:${PATH}
ENV PIP_CONSTRAINT=/tmp/constraints.txt

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p "${CONDA_DIR}" && \
    rm -f /tmp/miniconda.sh

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

RUN conda install -y -n base conda-libmamba-solver && \
    conda config --set solver libmamba

RUN conda env create -f /dyme-md.yml && \
    conda clean -afy

RUN conda install -y -n dyme_nodes salilab::modeller && \
    conda clean --all -y

#########################################################################################################################
# STEP 3 - ENTRYPOINT AND SOURCES
#########################################################################################################################

COPY ./nodes/md_node/dyme-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/dyme-entrypoint.sh

ENV PATH=/usr/local/bin:/dyme_env/anaconda/envs/dyme_nodes/bin:${PATH}

COPY ./nodes/source/ /dyme_base/backend/dyme

ENTRYPOINT ["/usr/local/bin/dyme-entrypoint.sh"]
