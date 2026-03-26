#!/usr/bin/env bash

# This file is a simple wrapper for apptainer so you don't have to write a long 
# command every time you need to launch a dyme worker.
# 
# usage: ./launch_node.sh <nodetype MD|scavenger> <dbhostname> <path_to_dymeroot>
# Example:
# 
# ./launch_node.sh MD dymeserver /path/to/your/shared/dyme/root


#Author:     
#Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
#Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
#Technische Universität Dresden


set -e

# ==============================
# Config
# ==============================
SIF_IMAGE="dyme_node.sif" #if the path to the image is common to all nodes, change it here
CONTAINER_WORKDIR="/dyme_root" #internal in the container



# ==============================
# Usage
# ==============================
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <nodetype: MD|scavenger> <dbhostname> </path/to/dir>"
    exit 1
fi

NODETYPE="$1"
DBHOST="$2"
BINDPATH="$3"

# ==============================
# Check that we have aptainer
# ==============================

if command -v apptainer >/dev/null 2>&1; then
    # at least one exists → continue
    :
else
    echo "Error: Apptainer is not installed or available. Install before running"
    exit 1
fi

# ==============================
# Validate nodetype
# ==============================
if [[ "$NODETYPE" != "MD" && "$NODETYPE" != "scavenger" ]]; then
    echo "Error: nodetype must be 'MD' or 'scavenger'"
    exit 1
fi

# ==============================
# Sanity checks
# ==============================
if [ ! -f "$SIF_IMAGE" ]; then
    echo "Error: SIF image '$SIF_IMAGE' not found."
    echo "Modify this file"
    exit 1
fi

if [ ! -d "$BINDPATH" ]; then
    echo "Error: bind path '$BINDPATH' does not exist"
    exit 1
fi

# ==============================
# Launch
# ==============================
echo "Launching DYME worker"
echo "Type: $NODETYPE | DB: $DBHOST | Bind: $BINDPATH"

if [ "$NODETYPE" = "MD" ]; then
    #Launch with --nv so GPU devices are passed to the container
    apptainer run --nv \
        --bind "$BINDPATH":"$CONTAINER_WORKDIR" \
        "$SIF_IMAGE" \
        "$NODETYPE" "$DBHOST"
else
    #Launch for CPU only
    apptainer run \
        --bind "$BINDPATH":"$CONTAINER_WORKDIR" \
        "$SIF_IMAGE" \
        "$NODETYPE" "$DBHOST"
fi