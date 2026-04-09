#"""
#DYME - Dynamic Mutagenesis Engine v1.0

#File:           Dockerfile
#Description:    Recipe to build the DYME Scavenger Node container

# DyME works exclusively on X86_64 hardware. Specially the MD node.

#Author:     
#Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
#Structural Bioinformatics Laboratory 
#BIOTEC - Pisabarro Group
#Technische Universität Dresden
#June 2024


# Use Ubuntu 20.04 as base
FROM ubuntu:20.04

LABEL authors="Pedro Guillem-Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>"
LABEL vendor="Structural Bioinformatics - Pisabarro Group - TU Dresden"
LABEL version="1.0"
LABEL description="DYME: Dynamic Mutagenesis Engine - Scavenger Node"
LABEL license="GPLv3"

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system utilities/compilers/MPIs/etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    mpirun \
    git \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda (or Mambaforge if you prefer)
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/miniconda && \
    rm -f /tmp/miniconda.sh

ENV PATH="/opt/miniconda/bin:${PATH}"

# Install mamba as the solver in the base environment
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
 && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
 
RUN conda install -y -n base -c conda-forge conda-libmamba-solver mamba && \
    conda config --system --set solver libmamba

# Copy the conda environment YAML from the build context
# (Make sure dyme_scavenger.yml is present next to this Dockerfile.)
COPY dyme_scavenger.yml /tmp/dyme_scavenger.yml

# If the uploaded YAML has a prefix other than /dyme_node, you can adjust it via sed
# (By default, the YAML posted shows "prefix: /dyme_root", so we’ll rewrite it to /dyme_node below.)
#RUN sed -i 's|/dyme_root|/dyme_node|g' /tmp/dyme_scavenger.yml

# Create the conda environment in /dyme_node using the YAML
RUN mamba env create -f /tmp/dyme_scavenger.yml -p /dyme_node && \
    conda clean -afy

# Clone only the "nodes" directory from your git repository into /dyme_node
# (Adjust the repository URL/path as needed.)
RUN git clone --depth 1 https://github.com/yourorg/yourrepo.git /tmp/yourrepo && \
    mv /tmp/yourrepo/nodes /dyme_node && \
    rm -rf /tmp/yourrepo

# Set PYTHONPATH to include /dyme_node
ENV PYTHONPATH="/dyme_node:${PYTHONPATH}"

# Map /dyme_data to a host volume
VOLUME ["/dyme_data"]

# Copy in our custom entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script as the container’s entrypoint
ENTRYPOINT ["/entrypoint.sh"]
