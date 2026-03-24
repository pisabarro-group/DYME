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

FROM nvidia/cuda:12.3.0-base-ubuntu:22.04

LABEL authors="Pedro Guillem-Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>"
LABEL vendor="Structural Bioinformatics - Pisabarro Group - TU Dresden"
LABEL version="1.0"
LABEL description="DYME: Dynamic Mutagenesis Engine - Node Container"
LABEL license="GPLv3"

ARG MODELLER_LICENSE

ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES=nvidia.com/gpu=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility


#Install Miniconda
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 
	
RUN set -eux; \
    mkdir -p /dyme_base \
	mkdir -p /dyme_env \
	mkdir -p /dyme_root/nodes/source \
	mkdir -p /dyme_root/projects \
    mkdir -p /dyme_root/logs \
	mkdir - /mnt/ramdrive \
	mkdir -p /docker-entrypoint-initdb.d

#declare
VOLUME /dyme_root


#PEDRO - Remember to patch Modeller here!!
#/group/bioinfp_apps/anaconda/envs/openmm-env/lib/modeller-10.4/

COPY ./nodes/md_node/dyme_md.yml /dyme-md.yml
#Install Miniconda quietly
#Make conda executable    
ENV KEY_MODELLER=$MODELLER_LICENSE
ENV CONDA_DIR=/dyme_env/anaconda

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /dyme_env/anaconda


ENV PATH=$CONDA_DIR/bin:$PATH

# Accept ToS for Anaconda default channels (non-interactive)
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
 && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

#Keep things fast.. default solver sucks
RUN conda install -y -n base conda-libmamba-solver
RUN conda config --set solver libmamba

#Fix setuptools backport not working with importlib
COPY ./nodes/md_node/constraints.txt /tmp/constraints.txt
ENV PIP_CONSTRAINT=/tmp/constraints.txt

RUN conda env create -f /dyme-md.yml && conda clean -afy
RUN conda install -n dyme_nodes salilab::modeller
#Clean up
RUN conda clean --all -y
#clean installer
RUN rm -Rf ~/miniconda.sh

RUN conda init

#Copy the service startup file to the container
COPY ./nodes/md_node/dyme-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/dyme-entrypoint.sh
ENV PATH=/usr/local/bin:/dyme_env/anaconda/envs/dyme_nodes/bin:$PATH

#Copy Node Sources
COPY ./nodes/source/ /dyme_base/backend/dyme

ENTRYPOINT ["/usr/local/bin/dyme-entrypoint.sh"]
#SHELL bash
